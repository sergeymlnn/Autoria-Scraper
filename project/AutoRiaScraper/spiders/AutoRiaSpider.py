from sys import exit
from typing import Iterator, Optional

import requests
from scrapy import Spider
from scrapy.http.response.html import HtmlResponse
from scrapy.loader import ItemLoader
from scrapy_splash import SplashRequest
from scrapy.settings import Settings
# from scrapy.shell import inspect_response
from scrapy.utils.project import get_project_settings

from AutoRiaScraper.args import SpiderArgs
from AutoRiaScraper.items import Car
from AutoRiaScraper.utils import gen_next_page_url


class AutoRiaSpider(Spider):
  """Spider to parse info about cars"""
  name = "autoria_spider"
  allowed_domains = ["auto.ria.com"]
  start_urls = ["https://auto.ria.com/uk/advanced-search"]

  def __init__(self, *args: str, **kwargs: str) -> None:
    """
    1) Read LUA-scripts used with a different types of webpages using Splash:
      - main form with the search filters;
      - category pages;
      - car pages.

    2) Init object to get access to the project settings.

    3) Object contating input spider arguments to base the search-filters on.

    Note: If the spider is unable to connect to the Splash, the process
          will be terminated. Check logs for more details.

    :param args: input spider args
    :param settings: project settings
    :param lua_main_page_handle_form: LUA-script to handle advanced search
    :param lua_category_page_script: LUA-script to handle category pages
    :param lua_car_page_script: LUA-script to handle car pages
    :raises ValueError: unless any input argument is valid
    """
    super().__init__(*args, **kwargs)
    _scrapyd_job_id = kwargs.pop("_job", "")  # noqa
    self.settings: Settings = get_project_settings()

    # Verify connection with Splash
    splash_url = self.settings["SPLASH_URL"]
    try:
      requests.get(splash_url)
    except requests.exceptions.ConnectionError as err:
      self.logger.critical(
        f"Unable to connect to Splash ({splash_url}). Reason: {err}"
      )
      exit(1)

    # Declare & validate input spider args
    self.args = SpiderArgs(**kwargs)

    # Read LUA-scripts to be used with SplashRequests
    with open(self.settings["LUA_CATEGORY_PAGE_SCRIPT"], "rb") as f1, \
         open(self.settings["LUA_CAR_PAGE_SCRIPT"], "rb") as f2, \
         open(self.settings["LUA_MAIN_PAGE_HANDLE_FORM"], "rb") as f3:
      self.lua_category_page_script = f1.read().decode("utf-8")
      self.lua_car_page_script = f2.read().decode("utf-8")
      self.lua_main_page_handle_form = f3.read().decode("utf-8")

  def start_requests(self) -> Iterator[SplashRequest]:
    """
    Set search-filters (using LUA-script) based on the input
    spider arguments and run the search.

    Note: input spider args containing None-values are ignored.
    """
    form_args = {k: v for k, v in self.args.__dict__.items() if v}
    yield SplashRequest(
      url=self.start_urls[0],
      endpoint="execute",
      callback=self.parse_cars,
      args={"lua_source": self.lua_main_page_handle_form, **form_args},
    )

  def parse_cars(self, response: HtmlResponse) -> Optional[Iterator[SplashRequest]]:
    """
    Iterate over a list of cars preserving pagination and perform
    requests to each car individually.

    Note (1): after submitting the form with filters the actual URL
              of the page can't be extract using 'response.url' due
              to AJAX, so we explicitly extract it using XPATH.
              However, such an option is available after paginating
              on the 2nd page.

    Note (2): we use a custom function to generate a URL to the next page.
              It prevents the Splash from scrolling the page down to extract
              the URL there.
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

    # Perform a requests to the car pages
    self.logger.info(f"Found {len(cars)} cars in {current_page_url}")
    car_urls = map(response.urljoin, cars.getall())
    for url in car_urls:
      yield SplashRequest(
        url,
        endpoint="execute",
        args={"lua_source": self.lua_car_page_script},
        cache_args=["lua_source"],
        callback=self.parse_car,
        meta=meta,
      )

    # Pagination
    next_page_url = gen_next_page_url(current_page_url)
    yield SplashRequest(
      next_page_url,
      endpoint="execute",
      args={"lua_source": self.lua_category_page_script},
      cache_args=["lua_source"],
      callback=self.parse_cars,
      meta=meta,
    )

  def parse_car(self, response: HtmlResponse) -> Iterator[Car]:
    """
    Collect info about specific car.

    Note: brand, model & year might be missing if the car was shipped
          from Europe (peculiarity of the website).
    """
    # inspect_response(response, self)
    brand_model_year = response.xpath("//span[@class='argument d-link__name']/text()")
    if not brand_model_year:
      self.logger.critical(f"Missing brand, model & year of the car in {response.url}")
      return
    brand, model, year = brand_model_year.get().strip().split(" ")
    car = ItemLoader(item=Car(), response=response)
    car.add_value("url", response.url)
    car.add_value("brand", brand)
    car.add_value("model", model)
    car.add_value("year", year)
    car.add_xpath("price", "//div[@class='price_value']/strong/text()")
    item = car.load_item()
    yield item
