from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LocationBase(BaseModel):
    name: str
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    latitude: float
    longitude: float
    timezone: str
    organization_id: UUID

class LocationCreate(LocationBase):
    ...

class Location(LocationBase):
    location_id: UUID
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True
