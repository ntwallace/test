from datetime import datetime, timezone, time as datetime_time
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.v1.hvac.schemas.hvac_schedule_mode import HvacScheduleMode


if TYPE_CHECKING:
    from app.v1.hvac.models.hvac_schedule import HvacSchedule
else:
    HvacSchedule = 'HvacSchedule'



class HvacScheduleEvent(Base):
    __tablename__ = 'hvac_schedule_events'

    hvac_schedule_event_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    hvac_schedule_id: Mapped[UUID] = mapped_column(ForeignKey('hvac_schedules.hvac_schedule_id', ondelete='CASCADE'))
    mode: Mapped[HvacScheduleMode] = mapped_column(String)
    time: Mapped[datetime_time] = mapped_column()
    set_point_c: Mapped[Optional[float]] = mapped_column()
    set_point_heating_c: Mapped[Optional[float]] = mapped_column()
    set_point_cooling_c: Mapped[Optional[float]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))

    hvac_schedule: Mapped[HvacSchedule] = relationship(back_populates='events')
