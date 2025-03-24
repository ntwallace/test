from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from typing import Optional


class HvacEquipmentTypeBase(BaseModel):
    make: str
    model: Optional[str] = None
    type: str
    subtype: Optional[str] = None
    year_manufactured: Optional[int] = None


class HvacEquipmentTypeCreate(HvacEquipmentTypeBase):
    pass


class HvacEquipmentType(HvacEquipmentTypeBase):
    hvac_equipment_type_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
