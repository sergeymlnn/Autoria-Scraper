from datetime import datetime
from typing import Any, Dict, Optional, Literal, List
from urllib.parse import urljoin

from itemloaders.processors import Join, MapCompose, TakeFirst
from scrapy import Item as ScrapyItem, Field as ScrapyField
from pydantic import BaseModel, Field, conint, validator
from scrapy.loader import ItemLoader


MAX_YEAR = datetime.now().year
MIN_YEAR = MAX_YEAR - 10

MIN_PRICE = 0


# Wrapper for ScrapyField, used on string fields, that returns the first valid
# value and eventually strips it.
DefaultStringField = lambda default = "": ScrapyField(
    default,
    input_processor=MapCompose(str.strip),
    output_processor=TakeFirst()
)


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
    cars_type: Literal["Всі", "Вживані", "Нові", "Під пригон"] = Field("Всі")
    use_splash: bool = Field(True, description="Tells the spider whether is should leverage Spalsh or not")

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


class CarItemsOnCategoryPage(ScrapyItem):
    """Item to extract car links on a category page and link to the next page"""
    current_page_url: str = DefaultStringField()
    next_page_url: str = DefaultStringField()
    car_urls_on_page: List[str] = ScrapyField(default=[])


class CarSellerItem(ScrapyItem):
    """Item to extract information about seller of a particular car"""
    name: str = DefaultStringField()
    last_online_time: str = DefaultStringField()
    location: str = DefaultStringField()
    verified_by_bank: bool = ScrapyField(default=False)
    phone_verified: bool = ScrapyField(default=True)
    signed_in_date: str = DefaultStringField()
    reputation: float = ScrapyField(default=0.0)
    total_clients_server: int = ScrapyField(default=0)


class CarSaleAdItem(ScrapyItem):
    """Item to extract additional information about car sale ad"""
    id: str = DefaultStringField()
    created_at: str = DefaultStringField()
    views: int = ScrapyField(default=0)
    saved: int = ScrapyField(default=0)


class CarItem(ScrapyItem):
    """Item to extract full information about a car"""
    link: str = DefaultStringField()
    brand: str = DefaultStringField()
    model: str = DefaultStringField()
    year: str = DefaultStringField()
    color: str = DefaultStringField()
    engine_capacity: str = DefaultStringField()
    last_repair: str = DefaultStringField()
    last_repair_info: str = DefaultStringField()
    total_owners: int = ScrapyField(default=1)
    remains_at_large: bool = ScrapyField(default=False)
    encumbrance_type: str = DefaultStringField()
    exclusion_limitations: str = DefaultStringField()
    official_mileage: float = ScrapyField(default=0.0)
    mileage_declared_by_seller: float = ScrapyField(default=0.0)
    mileage_fixation_date: str = DefaultStringField()
    mileage_fixation_source: str = DefaultStringField()
    has_crashes: bool = ScrapyField(default=False)
    crash_info: str = DefaultStringField()
    car_public_number: str = DefaultStringField()
    VIN: str = DefaultStringField()
    is_VIN_confirmed: bool = ScrapyField(default=False)
    tags: List[str] = ScrapyField(default=[])
    images: List[str] = ScrapyField(default=[])
    body_type: str = DefaultStringField()
    transmission_type: str = DefaultStringField()
    drive_unit: str = DefaultStringField()
    description: str = DefaultStringField()
    safety: str = DefaultStringField()
    comfort: str = DefaultStringField()
    multimedia: str = DefaultStringField()
    price: str = DefaultStringField()
    condition: str = DefaultStringField()
