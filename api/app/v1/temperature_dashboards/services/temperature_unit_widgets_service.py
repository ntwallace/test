from typing import List, Optional
from uuid import UUID

from app.v1.temperature_dashboards.repositories.temperature_unit_widgets_repository import TemperatureUnitWidgetsRepository
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import TemperatureUnitWidget, TemperatureUnitWidgetCreate, TemperatureUnitWidgetUpdate


class TemperatureUnitWidgetsService:

    def __init__(self, temperature_unit_widgets_repository: TemperatureUnitWidgetsRepository):
        self.temperature_unit_widgets_repository = temperature_unit_widgets_repository
    
    def create_temperature_unit_widget(self, temperature_unit_widget_create: TemperatureUnitWidgetCreate) -> TemperatureUnitWidget:
        return self.temperature_unit_widgets_repository.create(temperature_unit_widget_create)
    
    def get_temperature_unit_widget(self, temperature_unit_widget_id: UUID) -> Optional[TemperatureUnitWidget]:
        return self.temperature_unit_widgets_repository.get(temperature_unit_widget_id)
    
    def get_temperature_unit_widgets_for_temperature_dashboard(self, temperature_dashboard_id: UUID) -> List[TemperatureUnitWidget]:
        return self.temperature_unit_widgets_repository.filter_by(temperature_dashboard_id=temperature_dashboard_id)
    
    def filter_by(self, **kwargs) -> List[TemperatureUnitWidget]:
        return self.temperature_unit_widgets_repository.filter_by(**kwargs)
    
    def update_temperature_unit_widget(self, temperature_unit_widget_id: UUID, temperature_unit_widget_update: TemperatureUnitWidgetUpdate) -> TemperatureUnitWidget:
        temperature_unit_widget = self.temperature_unit_widgets_repository.update(
            temperature_unit_widget_id=temperature_unit_widget_id,
            temperature_unit_widget_update=temperature_unit_widget_update
        )

        if temperature_unit_widget is None:
            raise ValueError(f'Temperature unit widget with id {temperature_unit_widget_id} not found')
        
        return temperature_unit_widget
