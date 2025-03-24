from datetime import time as datetime_time
from enum import StrEnum
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from app.v1.hvac.schemas.hvac_schedule import HvacScheduleDay
from app.v3_adapter.schemas import BaseResponse


class APIHvacScheduleMode(StrEnum):
    COOLING = 'Cooling'
    HEATING = 'Heating'
    AUTO = 'Auto'
    OFF = 'Off'

class APIHvacScheduleEvent(BaseModel):
    mode: APIHvacScheduleMode
    time: datetime_time
    set_point_c: Optional[float] = None
    set_point_heating_c: Optional[float] = None
    set_point_cooling_c: Optional[float] = None

class APIHvacSchedule(BaseModel):
    id: UUID
    name: str
    events: List[APIHvacScheduleEvent]


# API Responses
class PutHvacScheduleRequestBody(BaseModel):
    name: str
    events: List[APIHvacScheduleEvent]

class PutHvacScheduleResponseData(BaseModel):
    id: UUID
    name: str
    events: List[APIHvacScheduleEvent]

class PutHvacScheduleResponse(BaseResponse):
    data: PutHvacScheduleResponseData


class GetHvacScheduleAssignmentsResponseDataItem(BaseModel):
    id: UUID
    name: str
    days: List[HvacScheduleDay]

class GetHvacScheduleAssignmentsResponse(BaseResponse):
    data: List[GetHvacScheduleAssignmentsResponseDataItem]
