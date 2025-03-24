
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.v1.auth.schemas.location_access_grant import LocationAccessGrant


class UserLocationAccessGrant(Base):
    __tablename__ = 'user_location_access_grants'

    user_id: Mapped[UUID] = mapped_column(primary_key=True)
    location_id: Mapped[UUID] = mapped_column(primary_key=True)
    location_access_grant: Mapped[LocationAccessGrant] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
