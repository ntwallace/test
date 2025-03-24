
from typing import Any, Generic, Optional, TypeVar
from uuid import UUID
from pydantic import BaseModel, field_validator

from app.v3_adapter.schemas import BaseResponse


class GetMyAccountResponseData(BaseModel):
    id: UUID
    given_name: str
    family_name: str
    email: str
    phone_number: Optional[str]

class GetMyAccountResponse(BaseResponse):
    data: GetMyAccountResponseData


_ValueT = TypeVar('_ValueT')

class PatchMyAccountFieldChange(BaseModel, Generic[_ValueT]):
    new_value: _ValueT

class PatchMyAccountRequest(BaseModel):
    given_name: Optional[PatchMyAccountFieldChange[str]] = None
    family_name: Optional[PatchMyAccountFieldChange[str]] = None
    phone_number: Optional[PatchMyAccountFieldChange[Optional[str]]] = None

    @field_validator("phone_number")
    def phone_number_validator(cls, value: Any) -> Any:
        if isinstance(value, PatchMyAccountFieldChange) and value.new_value == "":
            raise ValueError("Phone number is required")
        return value

class PatchMyAccountResponseData(BaseModel):
    id: UUID
    given_name: str
    family_name: str
    email: str
    phone_number: Optional[str]

class PatchMyAccountResponse(BaseResponse):
    data: PatchMyAccountResponseData
