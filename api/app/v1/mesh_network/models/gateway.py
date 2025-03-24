from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Gateway(Base):
    __tablename__ = 'gateways'

    gateway_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    duid: Mapped[str] = mapped_column(unique=True)
    # TODO: Add model column
    location_id: Mapped[UUID] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))

    __table_args__ = (UniqueConstraint('location_id', 'name', name='_gateways_unique_table_constraint'), )
