from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class HvacDashboardBase(BaseModel):
    name: str
    location_id: UUID


class HvacDashboardCreate(HvacDashboardBase):
    ...


class HvacDashboard(HvacDashboardBase):
    hvac_dashboard_id: UUID
    created_at: datetime
    updated_at: datetime
