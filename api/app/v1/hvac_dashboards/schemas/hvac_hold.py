from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.v1.hvac.schemas.hvac_schedule_mode import HvacScheduleMode
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import HvacFanMode


class HvacHoldBase(BaseModel):
    control_zone_hvac_widget_id: UUID
    mode: HvacScheduleMode
    author: str = 'Dashboard'
    fan_mode: HvacFanMode
    set_point_c: Optional[float]
    set_point_auto_heating_c: Optional[float]
    set_point_auto_cooling_c: Optional[float]
    expire_at_estimated: datetime
    expire_at_actual: datetime


class HvacHoldCreate(HvacHoldBase):
    pass

class HvacHold(HvacHoldBase):
    hvac_hold_id: UUID
    created_at: datetime
    updated_at: datetime
    