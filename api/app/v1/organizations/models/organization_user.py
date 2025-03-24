from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OrganizationUser(Base):
    __tablename__ = 'organization_users'

    organization_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    user_id: Mapped[UUID] = mapped_column(primary_key=True)
    is_organization_owner: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
