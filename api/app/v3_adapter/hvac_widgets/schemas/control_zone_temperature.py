from datetime import datetime
from typing import List, NamedTuple, Optional
from uuid import UUID

from pydantic import BaseModel

from app.v3_adapter.schemas import BaseResponse


class GetControlZoneTemperaturesResponseDataControlZone(BaseModel):
    id: UUID
    name: str

class GetControlZoneTemperaturesResponseData(BaseModel):
    id: UUID
    control_zones: List[GetControlZoneTemperaturesResponseDataControlZone]

class GetControlZoneTemperaturesResponse(BaseResponse):
    data: GetControlZoneTemperaturesResponseData


class ZoneTemperatureReading(NamedTuple):
    timestamp: datetime
    temperature_c: Optional[float]

class ZoneTemperatureData(BaseModel):
    id: UUID | str
    name: str
    readings: List[ZoneTemperatureReading]

class GetControlZoneTemperaturesDataResponseData(BaseModel):
    temperatures: List[ZoneTemperatureData]

class GetControlZoneTemperaturesDataResponse(BaseResponse):
    data: GetControlZoneTemperaturesDataResponseData