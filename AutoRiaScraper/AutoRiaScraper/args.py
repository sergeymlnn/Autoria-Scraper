from typing import List, Final, Optional

from attrs import define, field, validators


VEHICLE_CATEGORIES: Final[List[str]] = [
  "Будь-який", "Легкові", "Мото", "Вантажівки", "Причепи", "Спецтехніка",
  "Сільгосптехніка", "Автобуси", "Водний транспорт", "Повітряний транспорт",
  "Автобудинки",
]


@define(slots=False, frozen=True)
class SpiderArgs:
  """Provides & parses input spider arguments"""
  brand: str = field()
  model: Optional[str] = field(default=None)
  category: str = field(
    default=VEHICLE_CATEGORIES[0],
    validator=validators.in_(VEHICLE_CATEGORIES)
  )
