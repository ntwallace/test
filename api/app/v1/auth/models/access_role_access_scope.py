from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.v1.schemas import AccessScope


class AccessRoleAccessScope(Base):
    __tablename__ = "access_role_access_scopes"

    access_role_id: Mapped[UUID] = mapped_column(primary_key=True)
    access_scope: Mapped[AccessScope] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
