from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AccessRole(Base):
    __tablename__ = 'access_roles'

    access_role_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
