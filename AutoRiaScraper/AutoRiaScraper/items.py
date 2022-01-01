import re
from datetime import datetime
from typing import Any, Dict, Optional, Literal, List
from urllib.parse import urljoin

from itemloaders.processors import Join, MapCompose, TakeFirst
from scrapy import Item as ScrapyItem, Field as ScrapyField
from pydantic import BaseModel, Field, conint, validator
from scrapy.loader import ItemLoader
from price_parser import parse_price


MAX_YEAR = datetime.now().year
MIN_YEAR = MAX_YEAR - 50

MIN_PRICE = 0


# Wrapper for ScrapyField, used on string fields, that returns the first valid
# value and eventually strips it.
DefaultStringField = lambda default = "": ScrapyField(
    default,
    input_processor=MapCompose(str.strip),
    output_processor=TakeFirst()
)


def align_descriptions(descriptions: List[str]) -> str:
    """Converts a description represented as a string in array-like form to a common string"""
    return " ".join(map(str.strip, descriptions))


def extract_price(price: str) -> Optional[float]:
    """Extracts price from the input string and returns float value or None"""
    if not price:
        return None
    return parse_price(price).amount_float


def extract_year(str_year: str) -> Optional[str]:
    """Extracts year from the string and returns it, whether the valus is between defined min and max year"""
    try:
        year = int(re.search(r"\d{4}", str_year).group())
        print("YEAR: ", year)
    except AttributeError:
        return None
    return year if MIN_YEAR < year < MAX_YEAR else None


def extract_date_from_text(text: str) -> Optional[str]:
    """
    Extracts date from the input text (if it's in) and returns date in changed format.
    Source format: %d.%m.%Y
    Output format: %Y-%m-%d
    
    """
    date = re.search(r"\d{2}.\d{2}.\d{4}", text)
    if date:
        return datetime.strptime(res, "%d.%m.%Y").strftime("%Y-%m-%d")


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
    signed_in_date: str = ScrapyField(
        default=None,
        input_processor=MapCompose(extract_date_from_text),
        output_processor=TakeFirst(),
    )
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
    model: str = DefaultStringField()
    brand: str = DefaultStringField()
    year: int = ScrapyField(
        default=MAX_YEAR,
        input_processor=MapCompose(extract_year),
        output_processor=TakeFirst(),
    )
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
    description: str = ScrapyField(
        default="",
        input_processor=MapCompose(align_descriptions),
        output_processor=TakeFirst(),
    )
    safety: str = DefaultStringField()
    comfort: str = DefaultStringField()
    multimedia: str = DefaultStringField()
    price: float = ScrapyField(
        default=0.0,
        input_processor=MapCompose(extract_price),
        output_processor=TakeFirst(),
    )
    condition: str = DefaultStringField()
