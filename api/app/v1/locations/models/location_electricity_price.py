from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from uuid import uuid4, UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# Prevent circular import: https://stackoverflow.com/a/75919462/4533335
if TYPE_CHECKING:
    from app.v1.locations.models.location import Location
else:
    Location = 'Location'


class LocationElectricityPrice(Base):
    __tablename__ = "location_electricity_prices"

    location_electricity_price_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    location_id: Mapped[UUID] = mapped_column(ForeignKey("locations.location_id"))
    comment: Mapped[Optional[str]] = mapped_column()
    price_per_kwh: Mapped[float] = mapped_column()
    started_at: Mapped[datetime] = mapped_column()
    ended_at: Mapped[Optional[datetime]] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))

    location: Mapped[Location] = relationship(back_populates="electricity_prices")
