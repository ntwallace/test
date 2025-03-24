from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class HvacZoneBase(BaseModel):
    name: str
    location_id: UUID


class HvacZoneCreate(HvacZoneBase):
    pass


class HvacZone(HvacZoneBase):
    hvac_zone_id: UUID
    created_at: datetime
    updated_at: datetime
