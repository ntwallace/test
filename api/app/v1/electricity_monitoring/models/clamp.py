from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.v1.electricity_monitoring.schemas.clamp import ClampPhaseEnum


class Clamp(Base):
    __tablename__ = "clamps"

    clamp_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    port_name: Mapped[str] = mapped_column()
    port_pin: Mapped[int] = mapped_column()
    amperage_rating: Mapped[int] = mapped_column()
    phase: Mapped[ClampPhaseEnum] = mapped_column(String)
    circuit_id: Mapped[UUID] = mapped_column()
    electric_sensor_id: Mapped[UUID] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))
    
    __table_args__ = (UniqueConstraint('electric_sensor_id', 'port_name', 'port_pin', name='_clamps_unique_table_constraint'), )
