from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrganizationUserBase(BaseModel):
    organization_id: UUID
    user_id: UUID
    is_organization_owner: bool = False

class OrganizationUserCreate(OrganizationUserBase):
    pass

class OrganizationUser(OrganizationUserBase):
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
