from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.v1.appliances.schemas.appliance_type import ApplianceSuperTypeEnum


class ApplianceBase(BaseModel):
    name: str
    appliance_super_type: ApplianceSuperTypeEnum
    appliance_type_id: UUID
    location_id: UUID
    circuit_id: UUID
    temperature_sensor_place_id: UUID | None = None
    serial: str | None = None

class ApplianceCreate(ApplianceBase):
    pass


class Appliance(ApplianceBase):
    appliance_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
