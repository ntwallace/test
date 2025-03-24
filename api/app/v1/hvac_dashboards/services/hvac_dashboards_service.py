from typing import List, Optional
from uuid import UUID

from app.v1.hvac_dashboards.repositories.hvac_dashboards_repository import HvacDashboardsRepository
from app.v1.hvac_dashboards.schemas.hvac_dashboard import HvacDashboard, HvacDashboardCreate


class HvacDashboardsService:

    def __init__(self, hvac_dashboards_repository: HvacDashboardsRepository):
        self.hvac_dashboards_repository = hvac_dashboards_repository
    
    def create_hvac_dashboard(self, hvac_dashboard_create: HvacDashboardCreate) -> HvacDashboard:
        return self.hvac_dashboards_repository.create(hvac_dashboard_create)
        
    
    def get_hvac_dashboard(self, hvac_dashboard_id: UUID) -> Optional[HvacDashboard]:
        return self.hvac_dashboards_repository.get(hvac_dashboard_id)

    def get_hvac_dashboards_for_location(self, location_id: UUID) -> List[HvacDashboard]:
        return self.hvac_dashboards_repository.filter_by(location_id=location_id)
    
    def filter_by(self, **kwargs) -> List[HvacDashboard]:
        return self.hvac_dashboards_repository.filter_by(**kwargs)
