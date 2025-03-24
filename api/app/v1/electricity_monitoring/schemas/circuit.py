from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from enum import StrEnum


class CircuitTypeEnum(StrEnum):
    main = "main"
    neutral = "neutral"
    branch = "branch"


class CircuitBase(BaseModel):
    name: str
    electric_panel_id: UUID
    type: CircuitTypeEnum

class CircuitUpdate(BaseModel):
    circuit_id: UUID
    name: str

class CircuitCreate(CircuitBase):
    pass


class Circuit(CircuitBase):
    circuit_id: UUID
    created_at: datetime
    updated_at: datetime
