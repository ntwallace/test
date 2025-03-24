from datetime import datetime, timezone
from uuid import uuid4, UUID
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.database import Base


class ApplianceType(Base):
    __tablename__ = 'appliance_type'

    appliance_type_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    make: Mapped[str] = mapped_column()
    model: Mapped[Optional[str]] = mapped_column()
    type: Mapped[str] = mapped_column()
    subtype: Mapped[Optional[str]] = mapped_column()
    year_manufactured: Mapped[Optional[int]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint('make', 'model', 'type', 'subtype', 'year_manufactured', name='_appliance_type_unique_table_constraint'),)
