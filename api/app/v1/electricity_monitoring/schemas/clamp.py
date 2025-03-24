from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from enum import StrEnum


class ClampPhaseEnum(StrEnum):
    A = "A"
    B = "B"
    C = "C"
    N = "N"


class ClampBase(BaseModel):
    name: str
    port_name: str
    port_pin: int
    amperage_rating: int
    phase: ClampPhaseEnum
    circuit_id: UUID
    electric_sensor_id: UUID


class ClampCreate(ClampBase):
    pass


class Clamp(ClampBase):
    clamp_id: UUID
    created_at: datetime
    updated_at: datetime
