from typing import List, Optional
from uuid import UUID

from app.v1.electricity_dashboards.repositories.energy_consumption_breakdown_electric_widgets_repository import EnergyConsumptionBreakdownElectricWidgetRepository
from app.v1.electricity_dashboards.schemas.energy_consumption_breakdown_electric_widget import EnergyConsumptionBreakdownElectricWidget, EnergyConsumptionBreakdownElectricWidgetCreate


class EnergyConsumptionBreakdownElectricWidgetsService:

    def __init__(
        self,
        repository: EnergyConsumptionBreakdownElectricWidgetRepository
    ):
        self._repository = repository
    
    def create_energy_consumption_breakdown_electric_widget(self, energy_consumption_breakdown_electric_widget_create: EnergyConsumptionBreakdownElectricWidgetCreate) -> EnergyConsumptionBreakdownElectricWidget:
        return self._repository.create(energy_consumption_breakdown_electric_widget_create)

    def get_energy_consumption_breakdown_electric_widget(self, widget_id: UUID) -> Optional[EnergyConsumptionBreakdownElectricWidget]:
        return self._repository.get(widget_id)

    def get_energy_consumption_breakdown_electric_widgets_for_dashboard(self, dashboard_id: UUID) -> List[EnergyConsumptionBreakdownElectricWidget]:
        return self._repository.filter_by(electric_dashboard_id=dashboard_id)
