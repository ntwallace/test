from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ElectricityDashboardBase(BaseModel):
    name: str
    location_id: UUID 


class ElectricityDashboardCreate(ElectricityDashboardBase):
    pass


class ElectricityDashboard(ElectricityDashboardBase):
    electricity_dashboard_id: UUID
    created_at: datetime
    updated_at: datetime
