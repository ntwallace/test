from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class APIKeyAccessRole(Base):
    __tablename__ = "api_key_access_roles"

    api_key_id: Mapped[UUID] = mapped_column(primary_key=True)
    access_role_id: Mapped[UUID] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
