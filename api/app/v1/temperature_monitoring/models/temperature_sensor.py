from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4, UUID


from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.v1.temperature_monitoring.schemas.temperature_sensor import (
    TemperatureSensorMakeEnum,
    TemperatureSensorModelEnum,
)


class TemperatureSensor(Base):
    __tablename__ = 'temperature_sensors'

    temperature_sensor_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    duid: Mapped[str] = mapped_column(unique=True)
    make: Mapped[Optional[TemperatureSensorMakeEnum]] = mapped_column(String)
    model: Mapped[Optional[TemperatureSensorModelEnum]] = mapped_column(String)
    gateway_id: Mapped[UUID] = mapped_column()
    location_id: Mapped[UUID] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
