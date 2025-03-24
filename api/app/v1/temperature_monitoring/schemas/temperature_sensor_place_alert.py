from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TemperatureSensorPlaceAlertType(StrEnum):
    ABOVE_NORMAL_OPERATING_RANGE = 'above_normal_operating_range'
    BELOW_NORMAL_OPERATING_RANGE = 'below_normal_operating_range'

    def to_api_response_string(self):
        match (self):
            case self.ABOVE_NORMAL_OPERATING_RANGE:
                return 'High'
            case self.BELOW_NORMAL_OPERATING_RANGE:
                return 'Low'
            case _:
                return 'Unknown'

class TemperatureSensorPlaceAlertBase(BaseModel):
    temperature_sensor_place_id: UUID
    alert_type: TemperatureSensorPlaceAlertType
    threshold_temperature_c: float
    threshold_window_seconds: int
    reporter_temperature_c: float
    started_at: datetime
    ended_at: Optional[datetime]


class TemperatureSensorPlaceAlertCreate(TemperatureSensorPlaceAlertBase):
    pass


class TemperatureSensorPlaceAlert(TemperatureSensorPlaceAlertBase):
    temperature_sensor_place_alert_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
