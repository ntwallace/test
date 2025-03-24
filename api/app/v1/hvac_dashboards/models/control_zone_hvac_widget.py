from datetime import datetime, timezone
from typing import List, Optional
from uuid import uuid4, UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.v1.hvac_dashboards.models.control_zone_temperature_place_link import ControlZoneTemperaturePlaceLink
from app.v1.hvac.models.hvac_schedule import HvacSchedule


class ControlZoneHvacWidget(Base):
    __tablename__ = 'control_zone_hvac_widgets'

    hvac_widget_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    hvac_zone_id: Mapped[UUID] = mapped_column()

    monday_schedule_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('hvac_schedules.hvac_schedule_id', ondelete='SET NULL'))
    tuesday_schedule_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('hvac_schedules.hvac_schedule_id', ondelete='SET NULL'))
    wednesday_schedule_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('hvac_schedules.hvac_schedule_id', ondelete='SET NULL'))
    thursday_schedule_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('hvac_schedules.hvac_schedule_id', ondelete='SET NULL'))
    friday_schedule_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('hvac_schedules.hvac_schedule_id', ondelete='SET NULL'))
    saturday_schedule_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('hvac_schedules.hvac_schedule_id', ondelete='SET NULL'))
    sunday_schedule_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey('hvac_schedules.hvac_schedule_id', ondelete='SET NULL'))

    hvac_dashboard_id: Mapped[UUID] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))

    monday_schedule: Mapped[Optional[HvacSchedule]] = relationship(foreign_keys=[monday_schedule_id], passive_deletes=True)
    tuesday_schedule: Mapped[Optional[HvacSchedule]] = relationship(foreign_keys=[tuesday_schedule_id], passive_deletes=True)
    wednesday_schedule: Mapped[Optional[HvacSchedule]] = relationship(foreign_keys=[wednesday_schedule_id], passive_deletes=True)
    thursday_schedule: Mapped[Optional[HvacSchedule]] = relationship(foreign_keys=[thursday_schedule_id], passive_deletes=True)
    friday_schedule: Mapped[Optional[HvacSchedule]] = relationship(foreign_keys=[friday_schedule_id], passive_deletes=True)
    saturday_schedule: Mapped[Optional[HvacSchedule]] = relationship(foreign_keys=[saturday_schedule_id], passive_deletes=True)
    sunday_schedule: Mapped[Optional[HvacSchedule]] = relationship(foreign_keys=[sunday_schedule_id], passive_deletes=True)

    temperature_place_links: Mapped[List[ControlZoneTemperaturePlaceLink]] = relationship(back_populates='control_zone_hvac_widget', cascade='all, delete')
