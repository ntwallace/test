from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class TemperatureSensorPlaceReadingRaw(BaseModel):
    temperature_c: float
    timestamp_ms_utc: int
    battery_percentage: Optional[int]

class TemperatureSensorPlaceReading(BaseModel):
    temperature_sensor_place_id: UUID
    temperature_c: float
    battery_percentage: Optional[int]
    created_at: datetime
