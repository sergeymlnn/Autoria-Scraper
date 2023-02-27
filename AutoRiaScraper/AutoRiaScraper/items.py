from functools import partial
from typing import List, Optional

from itemloaders.processors import MapCompose, TakeFirst
from scrapy import Item as ScrapyItem, Field as ScrapyField

from AutoRiaScraper.utils import (
    extract_price_from_text,
    extract_year_from_text,
    extract_date_from_text,
    extract_integer_from_text,
)


# Aliases
ScrapyStrField = partial(
    ScrapyField,
    input_processor=MapCompose(lambda s: s if s is not None else ""),
    output_processor=TakeFirst()
)
ScrapyBooleanField = partial(
    ScrapyField,
    input_processor=MapCompose(bool),
    output_processor=TakeFirst()
)
ScrapyIntegerField = partial(
    ScrapyField,
    input_processor=MapCompose(extract_integer_from_text),
    output_processor=TakeFirst(),
)


class CarsListWithPagination(ScrapyItem):
    """Collects URLs on cars on a category page, category URL itself and URL to the next page"""
    current_page_url: str = ScrapyStrField()
    next_page_url: str = ScrapyStrField()
    car_urls_on_page: List[str] = ScrapyField(default=[])


class CarSellerItem(ScrapyItem):
    """Collects information about seller of a particular car"""
    name: str = ScrapyStrField()
    last_online_time: str = ScrapyStrField()
    location: str = ScrapyStrField()
    verified_by_bank: bool = ScrapyBooleanField()
    phone_verified: bool = ScrapyBooleanField()
    signed_in_date: str = ScrapyStrField(input_processor=MapCompose(extract_date_from_text))
    reputation: float = ScrapyField(default=0.0)
    is_company: bool = ScrapyBooleanField()
    company_location: str = ScrapyStrField()
    sold_cars: Optional[int] = ScrapyIntegerField()
    total_active_ads: Optional[int] = ScrapyIntegerField()
    total_verified_active_ads: Optional[int] = ScrapyIntegerField()
    company_website: str = ScrapyStrField()


class CarSaleAdItem(ScrapyItem):
    """Collects information about advertisement of a particular car on the website"""
    id: str = ScrapyStrField()
    created_at: str = ScrapyStrField()
    views: Optional[int] = ScrapyIntegerField()
    saved: Optional[int] = ScrapyIntegerField()


class CarItem(ScrapyItem):
    """Collects full information about car on its page"""
    link: str = ScrapyStrField()
    model: str = ScrapyStrField()
    brand: str = ScrapyStrField()
    year: int = ScrapyIntegerField(input_processor=MapCompose(extract_year_from_text))
    color: str = ScrapyStrField()
    engine_capacity: str = ScrapyStrField()
    last_repair: str = ScrapyStrField()
    last_repair_info: str = ScrapyStrField()
    total_owners: int = ScrapyIntegerField(default="1")
    remains_at_large: bool = ScrapyBooleanField()
    encumbrance_type: str = ScrapyStrField()
    exclusion_limitations: str = ScrapyStrField()
    official_mileage: float = ScrapyField(default=0.0)
    mileage_declared_by_seller: float = ScrapyStrField()
    mileage_fixation_date: str = ScrapyStrField()
    mileage_fixation_source: str = ScrapyStrField()
    has_crashes: bool = ScrapyBooleanField()
    crash_info: str = ScrapyStrField()
    car_public_number: str = ScrapyStrField()
    VIN: str = ScrapyStrField()
    is_VIN_confirmed: bool = ScrapyBooleanField()
    tags: List[str] = ScrapyField(default=[])
    images: List[str] = ScrapyField(default=[])
    body_type: str = ScrapyStrField()
    transmission_type: str = ScrapyStrField()
    drive_unit: str = ScrapyStrField()
    description: str = ScrapyStrField()
    safety: str = ScrapyStrField()
    comfort: str = ScrapyStrField()
    multimedia: str = ScrapyStrField()
    price: float = ScrapyField(
        default=0.0,
        input_processor=MapCompose(extract_price_from_text),
        output_processor=TakeFirst(),
    )
    condition: str = ScrapyStrField()
