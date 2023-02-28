from random import choice
from typing import List

import requests
from scrapy import Spider
from scrapy_splash.request import SplashRequest


def fetch_random_useragents() -> List[str]:
  """Fetches & returns a list of random User-Agents from Github"""
  r = requests.get(
    "https://raw.githubusercontent.com/sergeymlnn/Random-User-Agents-Database/main/useragents.txt"
  )
  useragents = r.text.split("\n")
  return list(map(str.strip, useragents))


class RandomUserAgentMiddleware:
  """Custom middleware to set a random User-Agent to each request"""
  __useragents: List[str] = fetch_random_useragents()

  def process_request(self, request: SplashRequest, spider: Spider) -> None:
    """Sets a random User-Agent into corresponding request header"""
    request.headers["User-Agent"] = choice(self.__useragents)
