from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ElectricSensor(Base):
    __tablename__ = "electric_sensors"

    electric_sensor_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    duid: Mapped[str] = mapped_column(unique=True)
    port_count: Mapped[int] = mapped_column()
    electric_panel_id: Mapped[Optional[UUID]] = mapped_column()
    gateway_id: Mapped[UUID] = mapped_column()
    a_breaker_num: Mapped[int] = mapped_column()
    b_breaker_num: Mapped[int] = mapped_column()
    c_breaker_num: Mapped[int] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint('name', 'gateway_id', 'electric_panel_id', name='_electric_sensors_unique_table_constraint'),)
