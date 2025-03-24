from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserAuthResetCode(Base):
    __tablename__ = 'user_auth_reset_codes'

    user_id: Mapped[UUID] = mapped_column(primary_key=True)
    reset_code: Mapped[UUID] = mapped_column()
    expires_at: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))
