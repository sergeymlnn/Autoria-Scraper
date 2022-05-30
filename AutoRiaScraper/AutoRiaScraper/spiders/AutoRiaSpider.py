from scrapy import Spider
from scrapy.http.response.html import HtmlResponse
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from scrapy.shell import inspect_response
from scrapy.utils.project import get_project_settings

from AutoRiaScraper.items import (
    CarItemsOnCategoryPage,
    CarSellerItem,
    CarSaleAdItem,
    CarItem,
)
from AutoRiaScraper.utils import gen_next_page_url
from AutoRiaScraper.SpiderArguments import SpiderArguments


class AutoriaSpider(Spider):
    """Spider to parse information about cars, based on specified filters from the main page"""
    name = 'autoria_spider'
    allowed_domains = ['auto.ria.com']
    start_urls = ['https://auto.ria.com/uk/']

    def __init__(self, *args, **kwargs) -> None:
        """
        Creates objects to get access to the project settings, input spider
        arguments and read LUA-scripts to set up behaviour of Splash requests,
        performed either on category pages of car pages.

        :param args: input spider arguments plus some default values
        :param settings: settings of the spider
        :param lua_category_page_script: lua-script to send Splash-request to the category pages
        :param car_page_script: lua-script to send Splash-request to the car pages
        :raises ValueError: unless any input argument contains invalid value
        """
        super().__init__(*args, **kwargs)
        self.args = SpiderArguments(**kwargs)
        self.settings = get_project_settings()
        with open(self.settings["LUA_CATEGORY_PAGE_SCRIPT"], "rb") as f1, \
             open(self.settings["LUA_CAR_PAGE_SCRIPT"], "rb") as f2, \
             open(self.settings["LUA_MAIN_PAGE_HANDLE_FORM"], "rb") as f3:
            self.lua_category_page_script = f1.read().decode("utf-8")
            self.car_page_script = f2.read().decode("utf-8")
            self.lua_main_page_handle_form = f3.read().decode("utf-8")

    def start_requests(self) -> None:
        """Performs splash-requests to the URLs of self.start_urls object """
        for url in self.start_urls:
            request = SplashRequest(
                url,
                endpoint="execute",
                cache_args=["lua_source"],
                callback=self.parse,
                args={
                    "lua_source": self.lua_main_page_handle_form,
                    "car_category": self.args.category
                },
            )
            yield request

    def parse(self, response: HtmlResponse, **kwargs) -> None:
        """
        Iterates over a list of cars on the category page and performs
        splash-requests to each individual car, plus preserves pagination
        on the category page.
        """
        # inspect_response(response, self)
        current_url = response.xpath("//link[@rel='canonical']/@href").get()
        item = ItemLoader(item=CarItemsOnCategoryPage(), response=response)
        item.add_value("current_page_url", current_url)
        item.add_xpath("car_urls_on_page", "//div[@class='item ticket-title']/a/@href")
        item.add_value("next_page_url", gen_next_page_url(current_url))
        loaded_item = item.load_item()
        if not loaded_item.get("car_urls_on_page"):
            self.logger.warning(f"Cars not found in {loaded_item['current_page_url']}")
            return
        for car_url in loaded_item["car_urls_on_page"]:
            car_page_request = SplashRequest(
                car_url,
                endpoint="execute",
                args={"lua_source": self.car_page_script},
                cache_args=["lua_source"],
                callback=self.parse_car_page,
                meta={"info": {"category_url": response.url}}
            )
            yield car_page_request
        next_page_request = SplashRequest(
            url=loaded_item["next_page_url"],
            endpoint="execute",
            args={"lua_source": self.lua_category_page_script},
            cache_args=["lua_source"],
            callback=self.parse
        )
        yield next_page_request

    def parse_car_page(self, response: HtmlResponse) -> None:
        """Collects full information about car and its seller on the car page"""
        # inspect_response(response, self)
        car_item = ItemLoader(item=CarItem(), response=response)
        car_item.add_value("link", response.url)
        car_item.add_xpath("model", "//h1[@class='head']/text()")
        car_item.add_xpath("brand", "//h1[@class='head']/span/text()")
        car_item.add_xpath("year", "//h1[@class='head']/text()")
        car_item.add_xpath("price", "//div[@class='price_value']/strong/text()")
        car_item.add_xpath("description", "//div[@class='full-description']/text()")

        # Each <dd> element contains 2 <span> elements inside
        # 1-st <span> with class 'label' is a spec name
        # 2-nd <span> with class 'argument' is a spec value
        technical_info = response.xpath("//div[contains(@class, 'technical-info')]/dl/dd")
        tech_cert_info = technical_info.xpath("./div[@class='t-check']")

        # Contains specifications of the car following the pattern: <spec_name>: <spec_value>
        technical_attr = "./span[@class='label']/text()"
        technical_attr_value = "./span[contains(@class, 'argument')]//text()"
        car_info = {
            spec.xpath(technical_attr).get(): " ".join(spec.xpath(technical_attr_value).getall())
            for spec in technical_info
        }

        description_specs = response.xpath("//div[@id='description_v3']/dl/dd")
        spec_attr_xpath = "./span[@class='label']/text()"
        spec_attr_value_xpath = "./span[@class='argument']//text()"
        additional_specs = {
            spec.xpath(spec_attr_xpath).get(): " ".join(spec.xpath(spec_attr_value_xpath).getall())
            for spec in description_specs
        }
        car_info.update(additional_specs)

        has_crashes = car_info.get("Участь в ДТП", "").lower() == "був в дтп"
        remains_at_large = not car_info.get("В розшуку", "").lower() == "ні"
        pb_number = tech_cert_info.xpath("./span[@class='state-num ua']/text()").get()
        vin_info = tech_cert_info.xpath("./span[@class='checked_ad label-check']/text()").get()
        is_vin_number_confirmed = "Перевірений VIN-код" in vin_info
        vin_number = tech_cert_info.xpath("./span[@class='label-vin']/text()").get()

        car_item.add_value("color", car_info.get("Колір"))
        car_item.add_value("engine_capacity", car_info.get("Двигун"))
        car_item.add_value("mileage_declared_by_seller", car_info.get("Пробіг"))
        car_item.add_value("multimedia", car_info.get("Мультимедіа"))
        car_item.add_value("comfort", car_info.get("Комфорт"))
        car_item.add_value("safety", car_info.get("Безпека"))
        car_item.add_value("drive_unit", car_info.get("Привід"))
        car_item.add_value("condition", car_info.get("Стан"))
        car_item.add_value("transmission_type", car_info.get("Коробка передач"))
        car_item.add_value("crash_info", car_info.get("Технічний стан"))
        car_item.add_value("total_owners", car_info.get("Кількість власників"))
        car_item.add_value("last_repair", car_info.get("Остання операція"))
        car_item.add_value("has_crashes", has_crashes)
        car_item.add_value("car_public_number", pb_number)
        car_item.add_value("remains_at_large", remains_at_large)
        car_item.add_value("is_VIN_confirmed", is_vin_number_confirmed)
        car_item.add_value("VIN", vin_number)

        # Information about seller
        seller_phone_verified = bool(
            response.xpath("(//div[@class='item_inner' and contains(., 'Перевірений банком')])[1]")
        )
        seller_verified_by_bank = bool(
            response.xpath("(//span[@data-tooltip='Особистість продавця встановлена банком'])[1]")
        )
        seller_is_company = bool(
            response.xpath(
                "(//div[contains(@class, 'seller_info_title') and contains(., 'Компанія')])[1]"
            )
        )

        # Information About Seller
        seller_item = ItemLoader(item=CarSellerItem(), response=response)
        seller_item.add_xpath("name", "(//h4[contains(@class, 'seller_info_name')])[1]//text()")
        seller_item.add_xpath("last_online_time", "(//div[@id='lastVisit'])[1]/strong/text()")
        seller_item.add_xpath(
            "location",
            "(//ul[contains(@class, 'checked-list')]/li)[1]/div/text()"
        )
        seller_item.add_xpath(
            "signed_in_date",
            # "(//span[contains(@data-tooltip, 'Продавець зареєстрований')])[1]/@data-tooltip"
            "(//ul[contains(@class, 'checked-list')]/li)[3]//text()"
        )
        seller_item.add_xpath(
            "reputation",
            "(//div[@class='item_inner' and contains(., 'оцінка продавця')])[1]/span[@class='bold']/text()"
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
        seller_item.add_value("verified_by_bank", seller_verified_by_bank)
        seller_item.add_value("phone_verified", seller_phone_verified)
        seller_item.add_value("is_company", seller_is_company)
        loaded_car_item_item = car_item.load_item()
        loaded_seller_item = seller_item.load_item()
        yield {**loaded_car_item_item, ** loaded_seller_item}
