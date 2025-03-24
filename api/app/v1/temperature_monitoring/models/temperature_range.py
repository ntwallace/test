from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.v1.temperature_monitoring.schemas.temperature_range import TemperatureRangeWarningLevelEnum


class TemperatureRange(Base):
    __tablename__ = 'temperature_ranges'

    temperature_range_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    high_degrees_celcius: Mapped[float] = mapped_column()
    low_degrees_celcius: Mapped[float] = mapped_column()
    warning_level: Mapped[TemperatureRangeWarningLevelEnum] = mapped_column(String)
    temperature_sensor_place_id: Mapped[UUID] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint('temperature_sensor_place_id', 'high_degrees_celcius', 'low_degrees_celcius', 'warning_level', name='_temperature_range_unique_table_constraint'),)
