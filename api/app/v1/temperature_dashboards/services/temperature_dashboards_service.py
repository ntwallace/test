from typing import List, Optional
from uuid import UUID

from app.v1.temperature_dashboards.repositories.temperature_dashboards_repository import TemperatureDashboardsRepository
from app.v1.temperature_dashboards.schemas.temperature_dashboard import TemperatureDashboard, TemperatureDashboardCreate


class TemperatureDashboardsService:

    def __init__(self, temperature_dashboards_repository: TemperatureDashboardsRepository):
        self.temperature_dashboards_repository = temperature_dashboards_repository
    
    def create_temperature_dashboard(self, temperature_dashboard_create: TemperatureDashboardCreate) -> TemperatureDashboard:
        return self.temperature_dashboards_repository.create(temperature_dashboard_create)
    
    def get_temperature_dashboard(self, temperature_dashboard_id: UUID) -> Optional[TemperatureDashboard]:
        return self.temperature_dashboards_repository.get(temperature_dashboard_id)
    
    def get_temperature_dashboards_for_location(self, location_id: UUID) -> List[TemperatureDashboard]:
        return self.temperature_dashboards_repository.filter_by(location_id=location_id)
    
    def filter_by(self, **kwargs) -> List[TemperatureDashboard]:
        return self.temperature_dashboards_repository.filter_by(**kwargs)
