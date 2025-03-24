from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4, UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.database import Base


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    email: Mapped[str] = mapped_column(unique=True)
    first_name: Mapped[str] = mapped_column()
    last_name: Mapped[str] = mapped_column()
    phone_number: Mapped[Optional[str]] = mapped_column() 
    password_hash: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
