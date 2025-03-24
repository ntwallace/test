from datetime import datetime, timezone
from typing import List
from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.v1.hvac.models.hvac_schedule_event import HvacScheduleEvent


class HvacSchedule(Base):
    __tablename__ = 'hvac_schedules'

    hvac_schedule_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    location_id: Mapped[UUID] = mapped_column()
    name: Mapped[str] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))

    events: Mapped[List[HvacScheduleEvent]] = relationship(back_populates='hvac_schedule', cascade='all,delete,delete-orphan')
