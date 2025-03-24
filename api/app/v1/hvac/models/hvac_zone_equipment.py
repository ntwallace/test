from datetime import datetime, timezone
from uuid import uuid4, UUID

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional

from app.database import Base


class HvacZoneEquipment(Base):
    __tablename__ = 'hvac_zone_equipment'

    hvac_zone_equipment_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    hvac_zone_id: Mapped[UUID] = mapped_column()
    hvac_equipment_type_id: Mapped[UUID] = mapped_column()
    circuit_id: Mapped[UUID] = mapped_column()
    serial: Mapped[Optional[str]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (UniqueConstraint('hvac_zone_id', 'hvac_equipment_type_id', name='_hvac_zone_equipment_unique_table_constraint'),)
