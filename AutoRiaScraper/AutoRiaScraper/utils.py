import re
from datetime import datetime
from typing import Optional, Union
from urllib.parse import urlparse, urlunparse, urlencode, parse_qsl

from price_parser import parse_price


def gen_next_page_url(url: str, param: str = "page") -> str:
  """
  Generates a URL to the next page using a GET-param named 'page',
  incrementing its current value or setting a default one unless
  the param is defined in the URL.

  Examples:
    Input URL: https://auto.ria.com/uk/search
    Output URL: https://auto.ria.com/uk/search?page=1
    ======================================================================
    Input URL: https://auto.ria.com/uk/search/?categories.main.id=1&page=4
    Output URL: https://auto.ria.com/uk/search/?categories.main.id=1&page=5

  :param url: URL to increment 'page' param or set the default one for
  :param param: name of the GET-param (page) to interact with
  :return: URL with the incremented or default value of the GET-param 'page'
  """
  url_parts = list(urlparse(url))
  page_param = re.search(fr"{param}=\d+", url_parts[4])
  page_group = {param: 0 if not page_param else int(page_param.group().split("=")[1])}
  page_group[param] += 1
  query = dict(parse_qsl(url_parts[4]), **page_group)
  url_parts[4] = urlencode(query)
  next_page_url = urlunparse(url_parts)
  return next_page_url


def extract_price_from_text(text: str) -> Optional[float]:
  """
  Extracts price from the input string and returns float value
  or None, unless the input string can be interpreted as a price.

  :param text: string to extract price from
  :return: price or None
  """
  if text:
    return parse_price(text).amount_float


def extract_year_from_text(text: str) -> Optional[int]:
  """
  Extracts and returns a 4-digits value from the input string
  to be considered as a year or None, unless a valid value is found.

  :param text: string to extract year from
  :return: year or None
  """
  year_group = re.search(r"\d{4}", text)
  if year_group:
    return int(year_group.group())


def extract_date_from_text(
  text: str,
  source_fmt: str = "%d.%m.%Y",
  output_fmt: str = "%Y-%m-%d"
) -> str:
  """
  Extracts date from the input text and returns it in a
  different format. Returns an empty string, unless date
  is found.

  Note: currently on the target website the date format is: '%d.%m.%Y'

  :param source_fmt: date format on the target website
  :param output_fmt: modified date format
  :param text: string to extract date from
  :return: date in the output format or empty string
  """
  date = re.search(r"\d{2}.\d{2}.\d{4}", text)
  if date:
    return datetime.strptime(date.group(), source_fmt).strftime(output_fmt)
  return ""


def extract_integer_from_text(text: str) -> Union[int, str]:
  """
  Extracts an integer number from the input string.
  Returns an empty string, unless  a number is found.

  :param text: string to extract an integer number from
  :return: an integer number or empty string
  """
  number_group = re.search(r"\d+", str(text))
  if number_group:
    return int(number_group.group())
  return ""
