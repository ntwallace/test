from datetime import datetime
from enum import StrEnum
from typing import Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationFeatureToggleEnum(StrEnum):
    ALERT_CENTER = 'alert-center'
    AUTO_CONFIGURE = 'autoconfigure'
    MANUAL_OVERRIDES = 'manual-overrides'
    AUTO_CHANGEOVER = 'autochangeover'
    ZONE_TEMPERATURES = 'zone-temperatures'

    @classmethod
    def from_str(cls, value: str) -> Self:
        return cls(value)


class OrganizationFeatureToggleBase(BaseModel):
    organization_id: UUID
    organization_feature_toggle: OrganizationFeatureToggleEnum
    is_enabled: bool

class OragnizationFeatureToggleCreate(OrganizationFeatureToggleBase):
    pass

class OrganizationFeatureToggleUpdate(OrganizationFeatureToggleBase):
    pass

class OrganizationFeatureToggle(OrganizationFeatureToggleBase):
    organization_feature_toggle_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
