from functools import partial
from typing import Optional

from itemloaders.processors import MapCompose, TakeFirst
from price_parser import parse_price
from scrapy import Item as ScrapyItem, Field as ScrapyField


def strip_str(s: str) -> str:
  """
  Convert the given value into str, remove leading & trailing
  whitespaces and return the value.

  Note: if the input value is falsy, an empty str will be returned!

  :param s: value to process
  :return: processed value or empty str
  """
  return "" if not s else str(s).strip()


def str_to_float(v: str) -> Optional[float]:
  """
  Convert the given str into float.

  Note: 'None' will be returned if the input value can't
        be interpreted as a float number!

  :param v: value to process
  :return: processed value or None
  """
  return parse_price(str(v)).amount_float


def str_to_int(v: str) -> Optional[int]:
  """
  Convert the given str into integer.

  Note: 'None' will be returned if the input value can't
        be interpreted as an integer number!

  :param v: value to process
  :return: processed value or None
  """
  try:
    return int("".join(x for x in str(v) if x.isdigit()))
  except ValueError:
    return None


# modified 'scrapy.Field' to be used with str-values
ScrapyStrField = partial(
  ScrapyField,
  input_processor=MapCompose(strip_str),
  output_processor=TakeFirst()
)

# modified 'scrapy.Field' to be used with float-values
ScrapyFloatField = partial(
  ScrapyField,
  input_processor=MapCompose(str_to_float),
  output_processor=TakeFirst()
)

# modified 'scrapy.Field' to be used with integer-values
ScrapyIntField = partial(
  ScrapyField,
  input_processor=MapCompose(str_to_int),
  output_processor=TakeFirst()
)


class Car(ScrapyItem):
  """Item to collect info about specific car"""
  brand: str = ScrapyStrField()
  model: str = ScrapyStrField()
  year: int = ScrapyIntField()
  price: float = ScrapyFloatField()
  url: str = ScrapyStrField()
