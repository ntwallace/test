from datetime import datetime
import re
from typing import Any
from uuid import UUID
from pydantic import BaseModel, field_validator

from app.v3_adapter.schemas import BaseResponse


class UserAuthResetCodeBase(BaseModel):
    user_id: UUID
    reset_code: UUID
    expires_at: datetime

class UserAuthResetCodeCreate(UserAuthResetCodeBase):
    ...

class UserAuthResetCodeUpdate(UserAuthResetCodeBase):
    ...

class UserAuthResetCode(UserAuthResetCodeBase):
    created_at: datetime
    updated_at: datetime


class AuthSessionResponseData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class AuthSessionResponse(BaseResponse):
    data: AuthSessionResponseData


class TokenRefreshRequestData(BaseModel):
    refresh_token: str

class TokenRefreshResponseData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'


class TokenRefreshResponse(BaseResponse):
    data: TokenRefreshResponseData


class PostResetCodeRequest(BaseModel):
    email: str

class PostResetCodeResponse(BaseResponse):
    data: None


class GetResetCodeResponse(BaseResponse):
    data: None


class PostAuthPasswordRequest(BaseModel):
    email: str
    code: UUID
    password: str

    @field_validator("password")
    def _password_validator(cls, value: Any) -> Any:
        if isinstance(value, str):
            if len(value) < 8:
                raise ValueError("Minimum 8 characters")
            if not re.match(r".*[0-9].*", value):
                raise ValueError("Number required")
            if not re.match(r".*[!\";#$%&'()*+,-./:;<=>?@\[\]\^_`{|}~].*", value):
                raise ValueError("Special symbol required")
        return value

class PostAuthPasswordResponse(BaseResponse):
    data: None