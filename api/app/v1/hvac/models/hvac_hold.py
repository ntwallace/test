from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4, UUID


from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.v1.hvac.schemas.hvac_schedule_mode import HvacScheduleMode
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import HvacFanMode


class HvacHold(Base):
    __tablename__ = 'hvac_holds'

    hvac_hold_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    control_zone_hvac_widget_id: Mapped[UUID] = mapped_column()
    mode: Mapped[HvacScheduleMode] = mapped_column(String)
    author: Mapped[str] = mapped_column(default='Dashboard')
    fan_mode: Mapped[HvacFanMode] = mapped_column(String)
    set_point_c: Mapped[Optional[float]] = mapped_column()
    set_point_auto_heating_c: Mapped[Optional[float]] = mapped_column()
    set_point_auto_cooling_c: Mapped[Optional[float]] = mapped_column()
    expire_at_estimated: Mapped[datetime] = mapped_column()
    expire_at_actual: Mapped[datetime] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
