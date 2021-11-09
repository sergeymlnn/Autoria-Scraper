from typing import Iterator, Dict
from pprint import pprint

from scrapy import Spider, Request
from scrapy.http.response.html import HtmlResponse
from scrapy.shell import inspect_response
from scrapy_splash import SplashRequest

from AutoRiaScraper.items import SpiderArguments


lua_script = """
    function main(splash, args)
        splash.private_mode_enabled = false
        splash.images_enabled = false
        splash.resource_timeout = 20.0

        assert(splash:go(args.url))

        function focus(sel)
            splash:select(sel):focus()
        end

        -- Wait until form is loaded to the page
        while not splash:select(".footer-form") do
            splash:wait(0.1)
        end

        -- focus("#categories")
        -- splash:send_text(splash.args.car_category)
        -- splash:select('.footer-form > button'):mouse_click()

        local carCategory = splash.args.car_category
        local carCategorySelect = splash:select('#categories')
        carCategorySelect:send_text(carCategory)
        assert(splash:wait(0.2))
        splash:select('.footer-form > button'):mouse_click()


        -- TOOD: Handle All Form Inputs

        -- local carBrand = splash.args.car_brand
        -- local carBrandInput = splash:select('#brandTooltipBrandAutocompleteInput-brand')
        -- carBrandInput:send_text(carBrand)
        -- assert(splash:wait(0.2))

        assert(splash:wait(3))
        return splash:html()
    end
"""


class AutoriaSpider(Spider):
    """Spdier to parse information about cars, based on specified filters from the main page"""
    name = 'autoria_spider'
    allowed_domains = ['auto.ria.com']
    start_urls = ['https://auto.ria.com/uk/']

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.args = SpiderArguments(**kwargs)

    def start_requests(self):
        """Performs either splash or default requests to the page with cars, according to the input spider arguments"""
        request_args = {
            "callback": self.parse,
        }
        for url in self.start_urls:
            request = Request(url, **request_args)
            if self.args.use_splash:
                request = SplashRequest(
                    **request_args,
                    url=url,
                    endpoint="execute",
                    args={
                        "lua_source": lua_script,
                        "car_category": self.args.category,
                        # "car_brand": self.args.brand,
                        # "car_model": self.args.model,
                    },
                    cache_args=["lua_source"],
                )
            yield request

    def parse(self, response: HtmlResponse) -> Iterator[Dict[str, str]]:
        """Iterates over car items and performs requests to each individual car page"""
        # inspect_response(response, self)
        yield {
            "status": "OK",
            "url": response.url,
        }
