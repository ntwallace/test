from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.v1.schemas import AccessScope


class AccessRoleAccessScopeBase(BaseModel):
    access_role_id: UUID
    access_scope: AccessScope


class AccessRoleAccessScopeCreate(AccessRoleAccessScopeBase):
    pass


class AccessRoleAccessScope(AccessRoleAccessScopeBase):
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )