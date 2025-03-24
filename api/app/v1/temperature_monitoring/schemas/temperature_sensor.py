from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TemperatureSensorMakeEnum(StrEnum):
    RUUVI = 'ruuvi'
    MINEW = 'minew'


class TemperatureSensorModelEnum(StrEnum):
    RUUVI_TAG = 'ruuvi_tag'
    S1 = 's1'
    MST01_01 = 'mst01-01'
    MST01_04 = 'mst01-04'


class TemperatureSensorBase(BaseModel):
    name: str
    duid: str
    make: Optional[TemperatureSensorMakeEnum] = Field(default=None)
    model: Optional[TemperatureSensorModelEnum] = Field(default=None)
    gateway_id: UUID
    location_id: UUID


class TemperatureSensorCreate(TemperatureSensorBase):
    pass


class TemperatureSensor(TemperatureSensorBase):
    temperature_sensor_id: UUID
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True
