from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from app.database import Base
from app.v1.schemas import AccessScope


class UserAccessScope(Base):
    __tablename__ = "user_access_scopes"

    user_id: Mapped[UUID] = mapped_column(primary_key=True)
    access_scope: Mapped[AccessScope] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
