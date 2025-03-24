from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class LocationElectricityPriceBase(BaseModel):
    location_id: UUID
    comment: Optional[str] = None
    price_per_kwh: float
    started_at: datetime
    ended_at: Optional[datetime] = None


class LocationElectricityPriceCreate(LocationElectricityPriceBase):
    pass

class LocationElectricityPriceUpdate(BaseModel):
    location_electricity_price_id: UUID
    ended_at: datetime


class LocationElectricityPrice(LocationElectricityPriceBase):
    location_electricity_price_id: UUID
    created_at: datetime
    updated_at: datetime
