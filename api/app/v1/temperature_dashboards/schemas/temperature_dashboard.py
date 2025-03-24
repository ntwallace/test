from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class TemperatureDashboardBase(BaseModel):
    name: str
    location_id: UUID


class TemperatureDashboardCreate(TemperatureDashboardBase):
    ...


class TemperatureDashboard(TemperatureDashboardBase):
    temperature_dashboard_id: UUID
    created_at: datetime
    updated_at: datetime
