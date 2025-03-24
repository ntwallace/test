from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserAccessRole(Base):
    __tablename__ = "user_access_roles"

    user_id: Mapped[UUID] = mapped_column(primary_key=True)
    access_role_id: Mapped[UUID] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
