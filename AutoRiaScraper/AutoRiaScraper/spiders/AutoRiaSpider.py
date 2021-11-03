from typing import *

from scrapy import Spider
from scrapy.http.response.html import HtmlResponse

from AutoRiaScraper.items import SpiderArguments


class AutoriaSpider(Spider):
  """Spdier to parse information about cars, based on specified filters from the main page"""
  name = 'autoria_spider'
  allowed_domains = ['auto.ria.com']
  start_urls = ['https://auto.ria.com/uk/']

  def __init__(self, *args, **kwargs):
    """"""
    super().__init__(*args, **kwargs)
    self.args = SpiderArguments(**kwargs)

  def parse(self, response: HtmlResponse) -> None:
    """"""
    yield {
      "status": "OK",
    }
