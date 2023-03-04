from itertools import count
from pathlib import Path
from typing import Any, Dict, Iterator

from scrapy import Spider
from scrapy.crawler import Crawler
from xlsxwriter.workbook import Workbook
from xlsxwriter.worksheet import Worksheet


class ItemsToExcelPipeline:
  """Pipeline to save collected items into excel-file"""

  def __init__(self, output_filepath: Path) -> None:
    """
    Creates an Excel workbook using path from the project settings,
    in order to save the scraped cars in.

    :param output_filepath: path to the file to save scraped cars in
    """
    self.workbook: Workbook
    self.worksheet: Worksheet
    self.output_filepath: Path = output_filepath
    self.counter: Iterator[int] = count(0)

  @classmethod
  def from_crawler(cls, crawler: Crawler) -> 'ItemsToExcelPipeline':
    """Sets path to the Excel workbook from the project settings"""
    return cls(output_filepath=crawler.settings.get("OUTPUT_FILEPATH"))

  def open_spider(self, spider: Spider) -> None:
    """Inits & opens the Excel workbook in order to save scraped items in"""
    self.workbook = Workbook(self.output_filepath)
    self.worksheet = self.workbook.add_worksheet()

  def close_spider(self, spider: Spider) -> None:
    """Closes the Excel workbook at the end of the scraping process"""
    self.workbook.close()

  def process_item(self, item: Dict[str, Any], spider: Spider) -> None:
    """Saves info about scraped cars into Excel file"""
    headers = list(item.keys())
    _counter = next(self.counter)
    if _counter == 0:
      for col in headers:
        self.worksheet.write(_counter, headers.index(col), col)
    else:
      for k, v in item.items():
        self.worksheet.write(_counter, headers.index(k), v)
      next(self.counter)
