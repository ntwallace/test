from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.v3_adapter.schemas import BaseResponse


class PatchCircuitRequestNameField(BaseModel):
    new_value: str

class PatchCircuitRequest(BaseModel):
    name: Optional[PatchCircuitRequestNameField] = None

class PatchCircuitResponseData(BaseModel):
    id: UUID
    name: str

class PatchCircuitResponse(BaseResponse):
    data: PatchCircuitResponseData