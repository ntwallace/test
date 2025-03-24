from datetime import datetime, time as datetime_time
from math import isnan
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.v1.hvac.schemas.hvac_schedule_mode import HvacScheduleMode


class HvacScheduleEventBase(BaseModel):
    mode: HvacScheduleMode
    time: datetime_time
    set_point_c: Optional[float]
    set_point_heating_c: Optional[float]
    set_point_cooling_c: Optional[float]

    @field_validator('set_point_c', 'set_point_heating_c', 'set_point_cooling_c')
    def change_nan_to_none(cls, v):
        if v is None or isnan(v):
            return None
        return v

class HvacScheduleEventCreate(HvacScheduleEventBase):
    pass

class HvacScheduleEvent(HvacScheduleEventBase):
    hvac_schedule_id: UUID
    hvac_schedule_event_id: UUID
    created_at: datetime
    updated_at: datetime