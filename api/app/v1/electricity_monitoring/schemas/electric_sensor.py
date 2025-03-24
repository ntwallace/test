from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ElectricSensorBase(BaseModel):
    name: str
    duid: str
    port_count: int
    electric_panel_id: Optional[UUID] = None
    gateway_id: UUID
    a_breaker_num: int
    b_breaker_num: int
    c_breaker_num: int


class ElectricSensorCreate(ElectricSensorBase):
    pass


class ElectricSensorPatch(BaseModel):
    name: Optional[str] = None


class ElectricSensor(ElectricSensorBase):
    electric_sensor_id: UUID
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True
