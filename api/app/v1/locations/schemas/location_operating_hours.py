from datetime import datetime, time
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.v1.schemas import DayOfWeek


class LocationOperatingHoursBase(BaseModel):
    location_id: UUID
    day_of_week: DayOfWeek
    is_open: bool = False
    work_start_time: Optional[time] = None
    open_time: Optional[time] = None
    close_time: Optional[time] = None
    work_end_time: Optional[time] = None


class LocationOperatingHoursCreate(LocationOperatingHoursBase):
    pass


class LocationOperatingHoursUpdate(LocationOperatingHoursBase):
    pass


class LocationOperatingHours(LocationOperatingHoursBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class LocationOperatingHoursMap(BaseModel):
    sunday: LocationOperatingHours
    monday: LocationOperatingHours
    tuesday: LocationOperatingHours
    wednesday: LocationOperatingHours
    thursday: LocationOperatingHours
    friday: LocationOperatingHours
    saturday: LocationOperatingHours
