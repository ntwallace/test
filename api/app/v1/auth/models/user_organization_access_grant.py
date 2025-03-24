from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.v1.auth.schemas.organization_access_grant import OrganizationAccessGrant


class UserOrganizationAccessGrant(Base):
    __tablename__ = 'user_organization_access_grants'

    user_id: Mapped[UUID] = mapped_column(primary_key=True)
    organization_id: Mapped[UUID] = mapped_column(primary_key=True)
    organization_access_grant: Mapped[OrganizationAccessGrant] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
