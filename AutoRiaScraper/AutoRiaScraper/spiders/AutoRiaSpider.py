from typing import Iterator, Dict
from pprint import pprint

from scrapy import Spider, Request
from scrapy.http.response.html import HtmlResponse
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from scrapy.shell import inspect_response

from AutoRiaScraper.items import (
    SpiderArguments,
    CarItemsOnCategoryPage,
    CarSellerItem,
    CarSaleAdItem,
    CarItem,
)


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
    start_urls = ['https://auto.ria.com/uk/auto_skoda_octavia_tour_31571325.html']

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.args = SpiderArguments(**kwargs)

    def start_requests(self):
        """Performs either splash or default scrapy requests to the page with cars, according to the input spider arguments"""
        request_args = {
            "callback": self.parse_car_page,
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
        # inspect_response(response, self)
        item = ItemLoader(item=CarItemsOnCategoryPage(), response=response)
        item.add_value("current_page_url", response.url)
        item.add_xpath("next_page_url", "//a[@class='page-link js-next ']/@href")
        item.add_xpath("car_urls_on_page", "//div[@class='item ticket-title']/a/@href")
        loaded_item = item.load_item()
        try:
            for car_url in loaded_item["car_urls_on_page"]:
                yield SplashRequest(
                    callback=self.parse_car_page,
                    url=car_url,
                    endpoint="execute",
                    args={
                        "lua_source": lua_script,
                    },
                    cache_args=["lua_source"],
                )
        except KeyError:
            self.logger.warning(f"Car items are missing in URL {loaded_item['current_page_url']}")
            return

        try:
            next_page_request = SplashRequest(
                callback=self.parse,
                url=loaded_item["next_page_url"],
                endpoint="execute",
                args={
                    "lua_source": lua_script,
                },
                cache_args=["lua_source"],
            )
        except KeyError:
            self.logger.warning("No pagination in URL {loaded_item['current_page_url']}")
            return
        yield next_page_request


    def parse_car_page(self, response: HtmlResponse):
        """Scrapes a page with a car on sale and collects all available information it"""
        # inspect_response(response, self)
        item = ItemLoader(item=CarItem(), response=response)
        item.add_value("link", response.url)
        item.add_xpath("model", "//h1[@class='head']/text()")
        item.add_xpath("brand", "//h1[@class='head']/span/text()")
        item.add_xpath("year", "//h1[@class='head']/text()")
        item.add_xpath("price", "//div[@class='price_value']/strong/text()")
        item.add_xpath("description", "//div[@id='full-description']/text()")

        # Each <dd> element contains 2 <span> elements inside
        # 1-st <span> with class 'label' is a spec name
        # 2-nd <span> with class 'argument' is a spec value
        specs_table = response.xpath("//div[@id='description_v3']/dl/dd")

        # A dict, that follows a pattern: <spec_name>: <spec_value>
        specs = {
            spec.xpath("./span[@class='label']/text()").get(): " ".join(spec.xpath("./span[@class='argument']//text()").getall())
            for spec in specs_table
        }

        item.add_value("color", specs.get("Колір"))
        item.add_value("engine_capacity", specs.get("Двигун"))
        item.add_value("mileage_declared_by_seller", specs.get("Пробіг"))
        item.add_value("multimedia", specs.get("Мультимедіа"))
        item.add_value("comfort", specs.get("Комфорт"))
        item.add_value("safety", specs.get("Безпека"))
        item.add_value("drive_unit", specs.get("Привід"))
        item.add_value("condition", specs.get("Стан"))
        item.add_value("transmission_type", specs.get("Коробка передач"))
        item.add_value("crash_info", specs.get("Технічний стан"))

        loaded_item = item.load_item()
        yield loaded_item
