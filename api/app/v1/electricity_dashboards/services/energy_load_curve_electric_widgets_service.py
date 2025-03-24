from typing import List, Optional
from uuid import UUID

from app.v1.electricity_dashboards.repositories.energy_load_curve_electric_widgets_repository import EnergyLoadCurveElectricWidgetsRepository
from app.v1.electricity_dashboards.schemas.energy_load_curve_electric_widget import EnergyLoadCurveElectricWidget, EnergyLoadCurveElectricWidgetCreate


class EnergyLoadCurveElectricWidgetsService:

    def __init__(
        self,
        repository: EnergyLoadCurveElectricWidgetsRepository
    ):
        self._repository = repository

    def create_energy_load_curve_electric_widget(self, energy_load_curve_electric_widget_create: EnergyLoadCurveElectricWidgetCreate) -> EnergyLoadCurveElectricWidget:
        return self._repository.create(energy_load_curve_electric_widget_create)
    
    def get_energy_load_curve_electric_widget(self, widget_id: UUID) -> Optional[EnergyLoadCurveElectricWidget]:
        return self._repository.get(widget_id)

    def get_energy_load_curve_electric_widgets_for_dashboard(self, dashboard_id: UUID) -> List[EnergyLoadCurveElectricWidget]:
        return self._repository.filter_by(electric_dashboard_id=dashboard_id)
