from typing import Optional

from attrs import asdict, define, field, validators

from AutoRiaScraper.settings import CURRENT_YEAR, MIN_YEAR, MIN_PRICE, CAR_TYPES


@define(slots=True, frozen=True)
class SpiderArguments:
  """Class to parse input arguments of the spider and return validated values"""
  brand: Optional[str] = None
  cars_type: str = field(default="Всі", converter=str.lower, validator=validators.in_(CAR_TYPES))
  category: str = field(default='Будь-який', converter=str.lower)
  max_price: float = field(default="inf", converter=float)
  max_year: int = field(default=CURRENT_YEAR, converter=int)
  min_price: float = field(default=MIN_PRICE, converter=float)
  min_year: int = field(default=MIN_YEAR, converter=int)
  model: Optional[str] = None
  region: Optional[str] = None
  verified_vin: bool = field(default=False, converter=bool)

  @min_price.validator
  def check_min_price(self, _, value: int) -> None:
    """Validates relevant of the value of min_price prop"""
    if value < MIN_PRICE:
      raise ValueError(f"Min price can't be less than {MIN_PRICE}")

  @max_year.validator
  @min_year.validator
  def check_min_year(self, _, value: int) -> None:
    """Validates relevance of values of min_year & max_year props"""
    if not MIN_YEAR <= value <= CURRENT_YEAR:
      raise ValueError(f"Min & Max year must be in range {MIN_YEAR} - {CURRENT_YEAR}")
    if value > self.max_year:
      raise ValueError(f"Min year can't be greater than max year")


if __name__ == '__main__':
  obj = SpiderArguments(
    min_year="2019",
    max_year="2020",
    min_price="23",
    max_price="35",
    verified_vin=1,
    cars_type="Під ПРигон",
  )
  print(asdict(obj))


