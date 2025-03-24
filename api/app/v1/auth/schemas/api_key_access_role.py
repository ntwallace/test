from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class APIKeyAccessRoleCreate(BaseModel):
    api_key_id: UUID
    access_role_id: UUID

class APIKeyAccessRole(APIKeyAccessRoleCreate):
    created_at: datetime
