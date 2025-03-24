from datetime import datetime
from typing import List, NamedTuple, Optional
from uuid import UUID

from pydantic import BaseModel

from app.v3_adapter.schemas import BaseResponse


class ZoneReading(NamedTuple):
    timestamp: datetime
    temperature_c: Optional[float]

class ZoneTrendData(BaseModel):
    zone: UUID
    name: str
    readings: List[ZoneReading]

class GetControlZoneTrendDataResponseData(BaseModel):
    zone_trends: List[ZoneTrendData]

class GetControlZoneTrendDataResponse(BaseResponse):
    data: GetControlZoneTrendDataResponseData
