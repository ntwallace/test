from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.v3_adapter.schemas import BaseResponse


class TemperatureUnitReading(BaseModel):
    last_reading: datetime
    temperature_c: float
    battery_percentage: Optional[int]


class TemperatureHistoricGraphReading(BaseModel):
    place: str
    timestamp: datetime
    temperature_c: float
    relative_humidity: float


class GetTemperatureHistoricGraphResponseData(BaseModel):
    data: Dict[str, str]
    readings: List[TemperatureHistoricGraphReading]


class GetTemperatureHistoricGraphDataResponse(BaseResponse):
    data: GetTemperatureHistoricGraphResponseData


class GetTemperatureUnitResponseData(BaseModel):
    id: UUID
    name: str
    appliance_type: str
    low_c: float
    high_c: float
    alert_threshold_s: int

class GetTemperatureUnitResponse(BaseModel):
    data: GetTemperatureUnitResponseData


class PutTemperatureUnitRequest(BaseModel):
    name: Optional[str] = None
    low_c: Optional[float] = None
    high_c: Optional[float] = None
    alert_threshold_s: Optional[int] = None
    appliance_type: Optional[str] = None

class PutTemperatureUnitResponseData(BaseModel):
    id: UUID
    name: str
    appliance_type: str
    low_c: float
    high_c: float
    alert_threshold_s: int

class PutTemperatureUnitResponse(BaseModel):
    data: PutTemperatureUnitResponseData


class GetTemperatureUnitDataResponseData(BaseModel):
    id: UUID
    temperature_place_id: UUID
    name: str
    appliance_type: str
    reading: Optional[TemperatureUnitReading]
    low_c: float
    high_c: float


class GetTemperatureUnitDataResponse(BaseResponse):
    data: GetTemperatureUnitDataResponseData
