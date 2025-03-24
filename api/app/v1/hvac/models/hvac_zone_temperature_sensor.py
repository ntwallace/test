from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class HvacZoneTemperatureSensors(Base):
    __tablename__ = 'hvac_zone_temperature_sensors'

    hvac_zone_temperature_sensor_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    hvac_zone_id: Mapped[UUID] = mapped_column()
    temperature_sensor_id: Mapped[UUID] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (UniqueConstraint('hvac_zone_id', 'temperature_sensor_id', name='_hvac_zone_temperature_sensor_unique_table_constraint'),)
