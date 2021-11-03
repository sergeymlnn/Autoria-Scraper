from datetime import datetime
from typing import *

from pydantic import BaseModel, Field, validator, conint


MAX_YEAR = datetime.now().year
MIN_YEAR = MAX_YEAR - 10

MIN_PRICE = 0
AVAILABLE_CAR_TYPES = ("Всі", "Вживані", "Нові", "Під пригон")


# //form[@id='mainSearchForm']/div/label[contains(text(),'Нові')]
class SpiderArguments(BaseModel):
  """Set and validates required search params of the filters bar from the main page to base the scraping process on"""
  category: Optional[str] = Field("Будь-який")
  brand: Optional[str] = Field(None)
  model: Optional[str] = Field(None)
  region: Optional[str] = Field(None)
  min_year: Optional[conint(ge=MIN_YEAR, le=MAX_YEAR)] = Field(MIN_YEAR)
  max_year: Optional[conint(ge=MIN_YEAR, le=MAX_YEAR)] = Field(MAX_YEAR)
  min_price: Optional[conint(ge=MIN_PRICE)] = Field(MIN_PRICE)
  max_price: Optional[int] = Field(None)
  verified_vin: Optional[bool] = Field(False)
  cars_type: Literal[AVAILABLE_CAR_TYPES] = Field("Всі")


  # TODO: Apply, when compatibility with lower-case in XPATH-expressions is provided
  # @validator('cars_type', pre=True, always=True)
  # def cars_type_to_lower(cls, v: str) -> str:
  #     """Adjusts the input car type to the string in lower case"""
  #     return v.lower()


  @validator('max_year')
  def validate_years(cls, v: int, values: Dict[str, Any]) -> int:
      """Verifies if the input min year is less than the specified max year"""
      assert v >= values["min_year"], "max year must be greater than min year"
      return v
    
  @validator('max_price')
  def validate_prices(cls, v: int, values: Dict[str, Any]) -> int:
      """Verifies if the input max year is greater than the specified min year"""
      assert v >= values["min_price"], "max price must be greater than min price"
      return v
