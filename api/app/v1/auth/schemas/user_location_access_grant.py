from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

from app.v1.auth.schemas.location_access_grant import LocationAccessGrant


class UserLocationAccessGrantBase(BaseModel):
    user_id: UUID
    location_id: UUID
    location_access_grant: LocationAccessGrant
    
class UserLocationAccessGrantCreate(UserLocationAccessGrantBase):
    pass

class UserLocationAccessGrant(UserLocationAccessGrantBase):
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
