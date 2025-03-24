from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

class GatewayBase(BaseModel):
    name: str
    duid: str
    location_id: UUID


class GatewayCreate(GatewayBase):
    pass


class GatewayPatch(BaseModel):
    name: Optional[str] = None


class Gateway(GatewayBase):
    gateway_id: UUID
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True
