from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, Field

from app.v1.schemas import DayOfWeek


class LocationTimeOfUseRateBase(BaseModel):
    location_id: UUID
    days_of_week: List[DayOfWeek]
    is_active: bool
    comment: str
    price_per_kwh: float
    day_started_at_seconds: int = Field(..., ge=0, le=86400)
    day_ended_at_seconds: int = Field(..., ge=1, le=86400)
    start_at: datetime
    end_at: datetime
    recurs_yearly: bool

class LocationTimeOfUseRateCreate(LocationTimeOfUseRateBase):
    pass

class LocationTimeOfUseRateUpdate(BaseModel):
    location_time_of_use_rate_id: UUID
    is_active: bool

class LocationTimeOfUseRate(LocationTimeOfUseRateBase):
    location_time_of_use_rate_id: UUID
    created_at: datetime
    updated_at: datetime
