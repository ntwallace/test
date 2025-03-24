from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from uuid import uuid4, UUID

from sqlalchemy import ARRAY, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.v1.schemas import DayOfWeek

if TYPE_CHECKING:
    from app.v1.locations.models.location import Location
else:
    Location = 'Location'


class LocationTimeOfUseRate(Base):
    __tablename__ = "location_time_of_use_rates"

    location_time_of_use_rate_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    location_id: Mapped[UUID] = mapped_column(ForeignKey("locations.location_id"))
    days_of_week: Mapped[List[DayOfWeek]] = mapped_column(ARRAY(String))
    is_active: Mapped[bool] = mapped_column(default=True)
    comment: Mapped[str] = mapped_column()
    price_per_kwh: Mapped[float] = mapped_column()
    day_started_at_seconds: Mapped[int] = mapped_column()
    day_ended_at_seconds: Mapped[int] = mapped_column()
    start_at: Mapped[datetime] = mapped_column()
    end_at: Mapped[datetime] = mapped_column()
    recurs_yearly: Mapped[bool] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))

    location: Mapped[Location] = relationship(back_populates="time_of_use_rates")
