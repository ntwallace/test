from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ControlZoneTrendReading(BaseModel):
    zone: UUID
    measure_datetime: datetime
    temperature_c: float

class ControlZoneTemperatureReading(BaseModel):
    telemetry: str
    measure_datetime: datetime
    reading: float
