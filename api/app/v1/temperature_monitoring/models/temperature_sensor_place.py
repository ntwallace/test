from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4, UUID

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import TemperatureSensorPlaceType


class TemperatureSensorPlace(Base):
    __tablename__ = 'temperature_sensor_places'

    temperature_sensor_place_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    temperature_sensor_place_type: Mapped[TemperatureSensorPlaceType] = mapped_column(String)
    location_id: Mapped[UUID] = mapped_column()
    temperature_sensor_id: Mapped[Optional[UUID]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))

    __table_args__ = (UniqueConstraint('location_id', 'name', name='_temperature_sensor_place_unique_table_constraint'), )
