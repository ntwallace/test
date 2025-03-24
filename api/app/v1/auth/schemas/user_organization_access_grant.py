from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.v1.auth.schemas.organization_access_grant import OrganizationAccessGrant


class UserOrganizationAccessGrantBase(BaseModel):
    user_id: UUID
    organization_id: UUID
    organization_access_grant: OrganizationAccessGrant
    
class UserOrganizationAccessGrantCreate(UserOrganizationAccessGrantBase):
    pass

class UserOrganizationAccessGrant(UserOrganizationAccessGrantBase):
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
