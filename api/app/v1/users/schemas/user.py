from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = None

class UserUpdate(BaseModel):
    user_id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]

class UserRead(UserBase):
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class User(UserRead):
    password_hash: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )
