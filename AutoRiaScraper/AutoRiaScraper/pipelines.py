from itertools import count
from typing import Union

import xlsxwriter
from scrapy.crawler import Crawler

from AutoRiaScraper.spiders.AutoRiaSpider import *


Item = dict[str, Union[int, float, bool, str, list[str]]]


class ItemsToExcelPipeline:
    """Pipeline to save collected items into excel-file"""

    def __init__(self, cars_excel_path):
        """
        Initializes path to the excel-workbook & defines counter
        to keep index of the latest inserted row
        """
        self.cars_excel_path = cars_excel_path
        self.worksheet = None
        self.workbook = None
        self.counter = count(0)

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> 'ItemsToExcelPipeline':
        """Reads path to the excel-workbook from the settings"""
        return cls(
            cars_excel_path=crawler.settings.get("CARS_EXCEL_PATH")
        )

    def open_spider(self, spider: 'AutoriaSpider') -> None:
        """Initializes and opens an excel-workbook to save scraped items in"""
        self.workbook = xlsxwriter.Workbook(self.cars_excel_path)
        self.worksheet = self.workbook.add_worksheet()

    def close_spider(self, spider: 'AutoriaSpider') -> None:
        """Closes the excel-workbook at the end of the scraping process"""
        self.workbook.close()

    def process_item(self, item: Item, spider: 'AutoriaSpider') -> None:
        """Writes collected items into excel-workbook"""
        headers = list(item.keys())
        _counter = next(self.counter)
        if _counter == 0:
            for col in headers:
                self.worksheet.write(_counter, headers.index(col), col)
        else:
            for k, v in item.items():
                self.worksheet.write(_counter, headers.index(k), v)
            next(self.counter)
