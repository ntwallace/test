from datetime import datetime, timezone
from uuid import uuid4, UUID


from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class OperatingRangeNotificationSettings(Base):
    __tablename__ = "operating_range_notification_settings"

    operating_range_notification_settings_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    user_id: Mapped[UUID] = mapped_column()
    location_id: Mapped[UUID] = mapped_column()
    allow_emails: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))

    __table_args__ = (UniqueConstraint("user_id", "location_id"),)
