from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4, UUID


from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.v1.temperature_monitoring.schemas.temperature_sensor_place_alert import TemperatureSensorPlaceAlertType


class TemperatureSensorPlaceAlert(Base):
    __tablename__ = 'temperature_sensor_place_alerts'

    temperature_sensor_place_alert_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    temperature_sensor_place_id: Mapped[UUID] = mapped_column()
    alert_type: Mapped[TemperatureSensorPlaceAlertType] = mapped_column(String)
    started_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    ended_at: Mapped[Optional[datetime]] = mapped_column()
    threshold_temperature_c: Mapped[float] = mapped_column()
    threshold_window_seconds: Mapped[int] = mapped_column()
    reporter_temperature_c: Mapped[float] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
