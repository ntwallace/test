from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class APIKeyCreate(BaseModel):
    name: str
    api_key_hash: str


class APIKey(APIKeyCreate):
    api_key_id: UUID
    created_at: datetime
    updated_at: datetime


# API Request/Response Models
class CreateAPIKeyRequest(BaseModel):
    name: str

class CreateAPIKeyResponse(BaseModel):
    api_key_id: UUID
    name: str
    api_key: str
    created_at: datetime
    updated_at: datetime
