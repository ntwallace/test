from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

from app.v1.schemas import AccessScope


class APIKeyAccessScopeCreate(BaseModel):
    api_key_id: UUID
    access_scope: AccessScope
    

class APIKeyAccessScope(APIKeyAccessScopeCreate):
    created_at: datetime
