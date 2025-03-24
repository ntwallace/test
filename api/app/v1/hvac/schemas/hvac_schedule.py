from datetime import datetime
from enum import StrEnum
from typing import List
from uuid import UUID

from pydantic import BaseModel

from app.v1.hvac.schemas.hvac_schedule_event import HvacScheduleEvent, HvacScheduleEventCreate


class HvacScheduleDay(StrEnum):
    MONDAY = 'Monday'
    TUESDAY = 'Tuesday'
    WEDNESDAY = 'Wednesday'
    THURSDAY = 'Thursday'
    FRIDAY = 'Friday'
    SATURDAY = 'Saturday'
    SUNDAY = 'Sunday'

class HvacMode(StrEnum):
    COOLING = 'Cool'
    HEATING = 'Heat'
    OFF = 'Off'


# Hvac Schedule
class HvacScheduleBase(BaseModel):
    location_id: UUID
    name: str

class HvacScheduleCreate(HvacScheduleBase):
    events: List[HvacScheduleEventCreate]

class HvacScheduleUpdate(BaseModel):
    name: str
    events: List[HvacScheduleEventCreate]

class HvacSchedule(HvacScheduleBase):
    hvac_schedule_id: UUID
    events: List[HvacScheduleEvent]
    created_at: datetime
    updated_at: datetime
