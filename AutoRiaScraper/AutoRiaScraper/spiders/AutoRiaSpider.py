from typing import Iterator, Dict
from pprint import pprint

from scrapy import Spider, Request
from scrapy.http.response.html import HtmlResponse
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest

from AutoRiaScraper.items import SpiderArguments, CarItemsOnCategoryPage


lua_script = """
    function main(splash, args)
        assert(splash:go(args.url))
        assert(splash:wait(3))
        return splash:html()
    end
"""


class AutoriaSpider(Spider):
    """Spdier to parse information about cars, based on specified filters from the main page"""
    name = 'autoria_spider'
    allowed_domains = ['auto.ria.com']
    start_urls = ['https://auto.ria.com/uk/bus/?page=1']

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
                    },
                    cache_args=["lua_source"],
                )
            yield request

    def parse(self, response: HtmlResponse) -> Iterator[Dict[str, str]]:
        """Iterates over car items and performs requests to each individual car page"""
        item = ItemLoader(item=CarItemsOnCategoryPage(), response=response)
        item.add_value("current_page_url", response.url)
        item.add_xpath("next_page_url", "//a[@class='page-link js-next ']/@href")
        item.add_xpath("car_urls_on_page", "//div[@class='item ticket-title']/a/@href")
        loaded_item = item.load_item()

        for car_url in loaded_item.car_urls_on_page:
            pass

        if loaded_item.next_page_url:
            yield Request(loaded_item.next_page_url, callback=self.parse)


    def parse_car_page(self, response: HtmlResponse):
        """"""
        pass
