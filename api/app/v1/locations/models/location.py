from datetime import datetime
from datetime import timezone as tz
from typing import List
from uuid import uuid4, UUID

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.database import Base
from app.v1.locations.models.location_electricity_price import LocationElectricityPrice
from app.v1.locations.models.location_operating_hours import LocationOperatingHours
from app.v1.locations.models.location_time_of_use_rate import LocationTimeOfUseRate


class Location(Base):
    __tablename__ = 'locations'

    location_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    state: Mapped[str] = mapped_column()
    zip_code: Mapped[str] = mapped_column()
    country: Mapped[str] = mapped_column()
    timezone: Mapped[str] = mapped_column()
    latitude: Mapped[float] = mapped_column()
    longitude: Mapped[float] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz.utc), onupdate=lambda: datetime.now(tz.utc))
    organization_id: Mapped[UUID] = mapped_column()

    operating_hours: Mapped[List[LocationOperatingHours]] = relationship(back_populates='location')
    electricity_prices: Mapped[List[LocationElectricityPrice]] = relationship(back_populates='location')
    time_of_use_rates: Mapped[List[LocationTimeOfUseRate]] = relationship(back_populates='location')
