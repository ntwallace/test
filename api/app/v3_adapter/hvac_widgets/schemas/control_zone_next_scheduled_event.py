from datetime import datetime
from enum import StrEnum
from typing import Literal, Optional

from pydantic import BaseModel

from app.v3_adapter.schemas import BaseResponse


class EventHvacMode(StrEnum):
    COOLING = 'Cooling'
    HEATING = 'Heating'
    OFF = 'Off'
    AUTO = 'Auto'


class GetControlZoneNextScheduledEventsResponseSimpleData(BaseModel):
    mode: Literal[EventHvacMode.COOLING, EventHvacMode.HEATING, EventHvacMode.OFF]
    time: datetime
    set_point_c: float

class GetControlZoneNextScheduledEventsResponseAutoData(BaseModel):
    mode: Literal[EventHvacMode.AUTO]
    time: datetime
    set_point_heating_c: float
    set_point_cooling_c: float


class GetControlZoneNextScheduledEventsResponse(BaseResponse):
    data: Optional[GetControlZoneNextScheduledEventsResponseSimpleData | GetControlZoneNextScheduledEventsResponseAutoData]
