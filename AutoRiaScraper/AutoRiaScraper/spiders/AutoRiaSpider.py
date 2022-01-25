from scrapy import Spider, Request
from scrapy.http.response.html import HtmlResponse
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from scrapy.shell import inspect_response

from AutoRiaScraper.items import (
    CarItemsOnCategoryPage,
    CarSellerItem,
    CarSaleAdItem,
    CarItem,
    SpiderArguments,
)


lua_script = """
    function main(splash, args)
        assert(splash:go(args.url))
        assert(splash:wait(3))
        return splash:html()
    end
"""


class AutoriaSpider(Spider):
    """Spider to parse information about cars, based on specified filters from the main page"""
    name = 'autoria_spider'
    allowed_domains = ['auto.ria.com']
    start_urls = ['']

    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.args = SpiderArguments(**kwargs)

    def start_requests(self) -> None:
        """
        Performs either splash or default scrapy requests to the page with cars,
        according to the input spider arguments
        """
        request_args = {"callback": self.parse_car_page}
        for url in self.start_urls:
            request = Request(url, **request_args)
            if self.args.use_splash:
                request = SplashRequest(
                    **request_args,
                    url=url,
                    endpoint="execute",
                    args={"lua_source": lua_script, },
                    cache_args=["lua_source"],
                )
            yield request


    def parse(self, response: HtmlResponse) -> None:
        """Iterates over a list of cars and performs requests to each individual car"""
        # inspect_response(response, self)
        item = ItemLoader(item=CarItemsOnCategoryPage(), response=response)
        item.add_value("current_page_url", response.url)
        item.add_xpath("next_page_url", "//a[@class='page-link js-next ']/@href")
        item.add_xpath("car_urls_on_page", "//div[@class='item ticket-title']/a/@href")
        loaded_item = item.load_item()
        if not loaded_item.get("car_urls_on_page"):
            self.logger.warning(f"Cars are missing in URL {loaded_item['current_page_url']}")
            return
        splash_request_params = {
            "endpoint": "execute",
            "args": {"lua_source": lua_script},
            "cache_args": ["lua_source"],
        }
        for car_url in loaded_item["car_urls_on_page"]:
            yield SplashRequest(car_url, callback=self.parse_car_page, **splash_request_params)
        if not loaded_item.get("next_page_url"):
            self.logger.warning(f"No pagination in URL {loaded_item['current_page_url']}")
            return
        next_page_request = SplashRequest(
            loaded_item["next_page_url"],
            callback=self.parse,
            **splash_request_params
        )
        yield next_page_request


    def parse_car_page(self, response: HtmlResponse) -> None:
        """Scrapes a page with a car on sale and collects all available information it"""
        # inspect_response(response, self)
        car_item = ItemLoader(item=CarItem(), response=response)
        car_item.add_value("link", response.url)
        car_item.add_xpath("model", "//h1[@class='head']/text()")
        car_item.add_xpath("brand", "//h1[@class='head']/span/text()")
        car_item.add_xpath("year", "//h1[@class='head']/text()")
        car_item.add_xpath("price", "//div[@class='price_value']/strong/text()")
        car_item.add_xpath("description", "//div[@id='full-description']/text()")

        # Each <dd> element contains 2 <span> elements inside
        # 1-st <span> with class 'label' is a spec name
        # 2-nd <span> with class 'argument' is a spec value
        specs_first_table = response.xpath("//div[@class='technical-info ticket-checked']/dl/dd")
        specs_second_table = response.xpath("//div[@id='description_v3']/dl/dd")
        car_certification_info = specs_first_table.xpath("./div[@class='t-check']")

        # Contains specifications of a car following the pattern: <spec_name>: <spec_value>
        spec_name_xpath = "./span[@class='label']/text()"
        spec_value_xpath = "./span[contains(@class, 'argument')]//text()"
        base_specs = {
            spec.xpath(spec_name_xpath).get(): " ".join(spec.xpath(spec_value_xpath).getall())
            for spec in specs_first_table
        }
        additional_spec_name_xpath = "./span[@class='label']/text()"
        additional_spec_value_xpath = "./span[@class='argument']//text()"
        additional_specs = {
            spec.xpath(additional_spec_name_xpath).get(): " ".join(spec.xpath(additional_spec_value_xpath).getall())
            for spec in specs_second_table
        }

        base_specs.update(additional_specs)

        car_item.add_value("color", base_specs.get("Колір"))
        car_item.add_value("engine_capacity", base_specs.get("Двигун"))
        car_item.add_value("mileage_declared_by_seller", base_specs.get("Пробіг"))
        car_item.add_value("multimedia", base_specs.get("Мультимедіа"))
        car_item.add_value("comfort", base_specs.get("Комфорт"))
        car_item.add_value("safety", base_specs.get("Безпека"))
        car_item.add_value("drive_unit", base_specs.get("Привід"))
        car_item.add_value("condition", base_specs.get("Стан"))
        car_item.add_value("transmission_type", base_specs.get("Коробка передач"))
        car_item.add_value("crash_info", base_specs.get("Технічний стан"))
        car_item.add_value("total_owners", base_specs.get("Кількість власників"))
        car_item.add_value("last_repair", base_specs.get("Остання операція"))
        car_item.add_value("has_crashes", True if base_specs.get("Участь в ДТП", "").lower() == "був в дтп" else False)
        car_item.add_value("remains_at_large", False if base_specs.get("В розшуку", "").lower() == "ні" else True)
        car_item.add_value(
            "car_public_number",
            car_certification_info.xpath("./span[@class='state-num ua']/text()").get()
        )
        car_item.add_value(
            "is_VIN_confirmed",
            True if car_certification_info.xpath("./span[@class='state-num ua']") else False
        )
        car_item.add_value(
            "VIN",
            car_certification_info.xpath("./span[@class='label-vin']/text()").get()
        )


        # Information about seller
        seller_item = ItemLoader(item=CarSellerItem(), response=response)
        seller_item.add_xpath("name", "(//h4[contains(@class, 'seller_info_name')])[1]//text()")
        seller_item.add_xpath("last_online_time", "(//div[@id='lastVisit'])[1]/strong/text()")
        seller_item.add_xpath("location", "(//ul[contains(@class, 'checked-list')]/li)[1]/div/text()")
        seller_item.add_xpath(
            "signed_in_date",
            "(//span[contains(@data-tooltip, 'Продавець зареєстрований')])[1]/@data-tooltip"
        )
        seller_item.add_value(
            "verified_by_bank",
            bool(response.xpath("(//span[@data-tooltip='Особистість продавця встановлена банком'])[1]"))
        )
        seller_item.add_value(
            "phone_verified",
            bool(response.xpath("(//div[@class='item_inner' and contains(., 'Перевірений банком')])[1]"))
        )
        seller_item.add_xpath(
            "reputation",
            "(//div[@class='item_inner' and contains(., 'оцінка продавця')])[1]/span[@class='bold']/text()"
        )
        seller_item.add_value(
            "is_company",
            bool(response.xpath("(//div[contains(@class, 'seller_info_title') and contains(., 'Компанія')])[1]"))
        )
        seller_item.add_xpath(
            "company_location",
            "(//div[@class='item_inner']/a[@class='map-loc']/text())[1]"
        )
        seller_item.add_xpath(
            "sold_cars",
            "(//div[@class='item_inner' and contains(., 'автомобілів')])[1]/text()"
        )
        seller_item.add_xpath(
            "total_active_ads",
            "(//div[@class='item_inner' and contains(., 'Пропозицій компанії')])[1]/a/text()"
        )
        seller_item.add_xpath(
            "total_verified_active_ads",
            "(//div[@class='item_inner' and contains(., 'Перевірених пропозицій')])[1]/a/text()"
        )
        seller_item.add_xpath(
            "company_website",
            "(//div[@class='item_inner' and contains(., 'Сайт компанії')])[1]/a/@href"
        )
        loaded_car_item_item = car_item.load_item()
        loaded_seller_item = seller_item.load_item()
        yield {**loaded_car_item_item, ** loaded_seller_item}
