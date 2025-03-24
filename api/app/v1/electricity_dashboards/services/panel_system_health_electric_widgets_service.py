from typing import List, Optional
from uuid import UUID

from app.v1.electricity_dashboards.repositories.panel_system_health_electric_widgets_repository import PanelSystemHealthElectricWidgetsRepository
from app.v1.electricity_dashboards.schemas.panel_system_health_electric_widget import PanelSystemHealthElectricWidget, PanelSystemHealthElectricWidgetCreate


class PanelSystemHealthElectricWidgetsService:

    def __init__(self, repository: PanelSystemHealthElectricWidgetsRepository):
        self.repository = repository

    def create_panel_system_health_electric_widget(self, panel_system_health_electric_widget_create: PanelSystemHealthElectricWidgetCreate) -> PanelSystemHealthElectricWidget:
        return self.repository.create(panel_system_health_electric_widget_create)
    
    def get_panel_system_health_electric_widget(self, electric_widget_id: UUID) -> Optional[PanelSystemHealthElectricWidget]:
        return self.repository.get(electric_widget_id)

    def get_panel_system_health_electric_widgets_for_dashboard(self, electric_dashboard_id: UUID) -> List[PanelSystemHealthElectricWidget]:
        return self.repository.filter_by(electric_dashboard_id=electric_dashboard_id)
