from typing import Iterator, Optional

from scrapy import Spider
from scrapy.http.response.html import HtmlResponse
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from scrapy.settings import Settings
from scrapy.shell import inspect_response
from scrapy.utils.project import get_project_settings

from AutoRiaScraper.args import SpiderArgs
from AutoRiaScraper.items import Car
from AutoRiaScraper.utils import gen_next_page_url


class AutoRiaSpider(Spider):
    """Spider to parse info about cars from https://auto.ria.com/"""
    name = "autoria_spider"
    allowed_domains = ["auto.ria.com"]
    start_urls = ["https://auto.ria.com/uk/advanced-search"]

    def __init__(self, *args, **kwargs) -> None:
      """
      Reads LUA-scripts to be used with a different types of webpages using Splash:
        1) form on the main page to parse filters;
        2) category pages;
        3) car pages.

      Also provides an attr to get access to the project settings.

      :param args: input spider args
      :param settings: project settings
      :param lua_main_page_handle_form: LUA-script used to handle advanced search filters
      :param lua_category_page_script: LUA-script used to handle category pages
      :param lua_car_page_script: LUA-script used to handle car pages
      :raises ValueError: unless any input argument is valid
      """
      super().__init__(*args, **kwargs)
      _scrapyd_job_id = kwargs.pop("_job", "")
      self.args = SpiderArgs(**kwargs)
      self.settings: Settings = get_project_settings()
      with open(self.settings["LUA_CATEGORY_PAGE_SCRIPT"], "rb") as f1, \
           open(self.settings["LUA_CAR_PAGE_SCRIPT"], "rb") as f2, \
           open(self.settings["LUA_MAIN_PAGE_HANDLE_FORM"], "rb") as f3:
        self.lua_category_page_script = f1.read().decode("utf-8")
        self.lua_car_page_script = f2.read().decode("utf-8")
        self.lua_main_page_handle_form = f3.read().decode("utf-8")
      
      breakpoint()

    def start_requests(self) -> Iterator[SplashRequest]:
      """
      Performs a request to the initial URL & configures
      the form with the search-filters according to the input
      spider args.

      Once the filters are set it submits the form, so it gets
      redirected to the page with the results of the search. 

      Note: input spider args containing None-values are ignored.
      """
      form_args = {k: v for k, v in self.args.__dict__.items() if v}
      yield SplashRequest(
        url=self.start_urls[0],
        endpoint="execute",
        callback=self.parse_cars,
        args={"lua_source": self.lua_main_page_handle_form, **form_args},
      )

    def parse_cars(self, response: HtmlResponse, **kwargs) -> Optional[Iterator[SplashRequest]]:
      """
      Iterates over a list of cars, generated after submitting the form
      with filters, preserving pagination & performs requests to each car
      individually.

      Note (1): after submitting the form, the actual URL of the page
                can not be extract by using 'response.url' due to AJAX,
                so we explicitly extract it using XPATH.
                Though after pagination can...

      Note (2): we use a custom function to generate a URL to the next page
                in order to not make Splash to scroll the current page to
                the bottom to extract a URL to the next page.
      """
      # inspect_response(response, self)
      current_page_url = response.url if "referer" in response.meta else \
        response.xpath("//a[@class='selectLang']/@href").get(response.url)
      cars = response.xpath("//div[@class='item ticket-title']/a/@href")
      if not cars:
        self.logger.critical(f"Cars not found in {current_page_url}")
        return

      # Request meta
      meta = {"referer": current_page_url}

      # Performing requests to the car pages
      self.logger.info(f"Found {len(cars)} cars in {current_page_url}")
      car_urls = map(response.urljoin, cars.getall())
      for url in car_urls:
        yield SplashRequest(url,
          endpoint="execute",
          args={"lua_source": self.lua_car_page_script},
          cache_args=["lua_source"],
          callback=self.parse_car_page,
          meta=meta
        )

      # Pagination
      next_page_url = gen_next_page_url(current_page_url)
      yield SplashRequest(next_page_url,
        endpoint="execute",
        args={"lua_source": self.lua_category_page_script},
        cache_args=["lua_source"],
        callback=self.parse_cars,
        meta=meta
      )

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
        vin_info = tech_cert_info.xpath("./span[@class='checked_ad label-check']/text()").get("")
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
