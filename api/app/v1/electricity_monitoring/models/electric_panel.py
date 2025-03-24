from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4, UUID

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanelTypeEnum


class ElectricPanel(Base):
    __tablename__ = "electric_panels"

    electric_panel_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    panel_type: Mapped[ElectricPanelTypeEnum] = mapped_column(String)
    location_id: Mapped[UUID] = mapped_column()
    breaker_count: Mapped[Optional[int]] = mapped_column()
    parent_electric_panel_id: Mapped[Optional[UUID]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (UniqueConstraint('name', 'location_id', name='_electric_panels_unique_table_constraint'), )
