from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.v1.schemas import AccessScope


class UserAccessScopeBase(BaseModel):
    user_id: UUID
    access_scope: AccessScope


class UserAccessScopeCreate(UserAccessScopeBase):
    pass


class UserAccessScope(UserAccessScopeBase):
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        frozen=True
    )
