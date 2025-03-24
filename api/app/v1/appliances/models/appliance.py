from datetime import datetime, timezone
from uuid import uuid4, UUID
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.database import Base
from app.v1.appliances.schemas.appliance_type import ApplianceSuperTypeEnum


class Appliance(Base):
    __tablename__ = 'appliances'

    appliance_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    appliance_super_type: Mapped[ApplianceSuperTypeEnum] = mapped_column(String)
    serial: Mapped[Optional[str]] = mapped_column(unique=True)
    appliance_type_id: Mapped[Optional[UUID]] = mapped_column()
    circuit_id: Mapped[Optional[UUID]] = mapped_column()
    temperature_sensor_place_id: Mapped[Optional[UUID]] = mapped_column()
    location_id: Mapped[UUID] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint('name', 'location_id', 'circuit_id'),)
