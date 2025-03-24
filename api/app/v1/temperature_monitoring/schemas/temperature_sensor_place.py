from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

class TemperatureSensorPlaceType(StrEnum):
    APPLIANCE = 'appliance'
    ZONE = 'zone'


class TemperatureSensorPlaceBase(BaseModel):
    name: str
    temperature_sensor_place_type: TemperatureSensorPlaceType
    location_id: UUID
    temperature_sensor_id: Optional[UUID] = None


class TemperatureSensorPlaceCreate(TemperatureSensorPlaceBase):
    pass


class TemperatureSensorPlacePatch(BaseModel):
    temperature_sensor_place_id: UUID
    temperature_sensor_id: Optional[UUID] = Field(default=None)


class TemperatureSensorPlace(TemperatureSensorPlaceBase):
    temperature_sensor_place_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
