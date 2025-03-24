from typing import List, Optional
from uuid import UUID

from app.v1.electricity_dashboards.repositories.electricity_dashboards_repository import ElectricityDashboardsRepository
from app.v1.electricity_dashboards.schemas.electricity_dashboard import ElectricityDashboard, ElectricityDashboardCreate


class ElectricityDashboardsService:

    def __init__(self, electricity_dashboards_repository: ElectricityDashboardsRepository):
        self.electricity_dashboards_repository = electricity_dashboards_repository
    
    def create_electricity_dashboard(self, electricity_dashboard_create: ElectricityDashboardCreate) -> ElectricityDashboard:
        return self.electricity_dashboards_repository.create_electricity_dashboard(electricity_dashboard_create)

    def get_electricity_dashboard(self, electricity_dashboard_id: UUID) -> Optional[ElectricityDashboard]:
        return self.electricity_dashboards_repository.get_electricity_dashboard(electricity_dashboard_id)

    def filter_by(self, **kwargs) -> List[ElectricityDashboard]:
        return self.electricity_dashboards_repository.filter_by(**kwargs)
