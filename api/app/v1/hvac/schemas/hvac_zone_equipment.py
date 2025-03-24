from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Optional


class HvacZoneEquipmentBase(BaseModel):
    hvac_zone_id: UUID
    hvac_equipment_type_id: UUID
    circuit_id: UUID
    serial: Optional[str] = None


class HvacZoneEquipmentCreate(HvacZoneEquipmentBase):
    pass


class HvacZoneEquipment(HvacZoneEquipmentBase):
    hvac_zone_equipment_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
