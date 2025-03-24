from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class TemperatureRangeWarningLevelEnum(StrEnum):
    GOOD = 'good'
    WARNING = 'warning'
    DANGER = 'danger'


class TemperatureRangeBase(BaseModel):
    high_degrees_celcius: float
    low_degrees_celcius: float
    warning_level: TemperatureRangeWarningLevelEnum
    temperature_sensor_place_id: UUID


class TemperatureRangeCreate(TemperatureRangeBase):
    pass


class TemperatureRange(TemperatureRangeBase):
    temperature_range_id: UUID
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True
