from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class UserAccessRoleBase(BaseModel):
    user_id: UUID
    access_role_id: UUID


class UserAccessRoleCreate(UserAccessRoleBase):
    pass


class UserAccessRole(UserAccessRoleBase):
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


# API Request/Response Schemas
class PostUserAccessRoleRequest(BaseModel):
    access_role_id: UUID
