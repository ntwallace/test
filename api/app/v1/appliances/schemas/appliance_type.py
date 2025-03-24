from datetime import datetime
from enum import StrEnum
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ApplianceSuperTypeEnum(StrEnum):
    FRIDGE = 'fridge'
    FREEZER = 'freezer'
    OTHER = 'other'


class ApplianceTypeBase(BaseModel):
    make: str
    model: str | None = None
    type: str
    subtype: str | None = None
    year_manufactured: int | None = None


class ApplianceTypeCreate(ApplianceTypeBase):
    pass


class ApplianceType(ApplianceTypeBase):
    appliance_type_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
