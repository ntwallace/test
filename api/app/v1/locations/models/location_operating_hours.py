from datetime import datetime, timezone, time
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.v1.schemas import DayOfWeek


# Prevent circular import: https://stackoverflow.com/a/75919462/4533335
if TYPE_CHECKING:
    from app.v1.locations.models.location import Location
else:
    Location = 'Location'


class LocationOperatingHours(Base):
    __tablename__ = 'location_operating_hours'

    location_id: Mapped[UUID] = mapped_column(ForeignKey("locations.location_id"), primary_key=True)
    day_of_week: Mapped[DayOfWeek] = mapped_column(String, primary_key=True)
    is_open: Mapped[bool] = mapped_column()
    work_start_time: Mapped[Optional[time]] = mapped_column()
    open_time: Mapped[Optional[time]] = mapped_column()
    close_time: Mapped[Optional[time]] = mapped_column()
    work_end_time: Mapped[Optional[time]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    location: Mapped[Location] = relationship(back_populates='operating_hours')
