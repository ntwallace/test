from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AccessRoleBase(BaseModel):
    name: str


class AccessRoleCreate(AccessRoleBase):
    pass


class AccessRole(AccessRoleBase):
    access_role_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )