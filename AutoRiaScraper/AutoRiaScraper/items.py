from functools import partial
from typing import Optional

from itemloaders.processors import MapCompose, TakeFirst
from price_parser import parse_price
from scrapy import Item as ScrapyItem, Field as ScrapyField


def strip_str(s: str) -> str:
  """
  Explicitly converts the input value into str,
  removes leading & trailing whitespaces, & returns the processed
  value.

  Note: if the input value is falsy, an empty str will be returned !

  :param s: input value to be interpreted as str 
  :return: str without leading & trailing whitespaces
  """
  return "" if not str else str(s).strip()


def str_to_float(v: str) -> Optional[float]:
  """
  Converts the input str value into float & returns it.

  Note: 'None' will be returned if the input value can not
        be interpreted as a float number !

  :param v: str to be converted into float
  :return: input value as a float number or 'None'
  """
  return parse_price(str(v)).amount_float
  

def str_to_int(v: str) -> Optional[int]:
  """
  Converts the input str value into float & returns it.

  Note: 'None' will be returned if the input value can not
        be interpreted as an integer !

  :param v: str to be converted into an integer
  :return: input value as an integer or 'None'
  """
  try:
    return int("".join(x for x in str(v) if x.isdigit()))
  except ValueError:
    return None
  

# modified 'scrapy.Field' to be used with str values
ScrapyStrField = partial(ScrapyField,
  input_processor=MapCompose(strip_str),
  output_processor=TakeFirst()
)

# modified 'scrapy.Field' to be used with float values
ScrapyFloatField = partial(ScrapyField,
  input_processor=MapCompose(str_to_float),
  output_processor=TakeFirst()
)

# modified 'scrapy.Field' to be used with integer values
ScrapyIntField = partial(ScrapyField,
  input_processor=MapCompose(str_to_int),
  output_processor=TakeFirst()
)


class Car(ScrapyItem):
  """Scrapy Item used to collect info about specific car"""
  brand: str = ScrapyStrField()
  model: str = ScrapyStrField()
  year: int = ScrapyIntField()
  price: float =  ScrapyFloatField()
  url: str = ScrapyStrField()
