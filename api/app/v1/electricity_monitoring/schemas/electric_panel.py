from datetime import datetime
from enum import StrEnum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

class ElectricPanelTypeEnum(StrEnum):
    mdp = "mdp"
    sub = "sub"


class ElectricPanelBase(BaseModel):
    name: str
    panel_type: ElectricPanelTypeEnum
    location_id: UUID
    breaker_count: Optional[int] = Field(default=None)
    parent_electric_panel_id: Optional[UUID] = Field(default=None)


class ElectricPanelCreate(ElectricPanelBase):
    pass

class ElectricPanel(ElectricPanelBase):
    electric_panel_id: UUID
    created_at: datetime
    updated_at: datetime
