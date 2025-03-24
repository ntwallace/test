from typing import List
from uuid import UUID

from app.v1.electricity_monitoring.repositories.electric_panels_repository import ElectricPanelsRepository
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanel, ElectricPanelCreate

class ElectricPanelsService:

    def __init__(self, electric_panels_repository: ElectricPanelsRepository):
        self.electric_panels_repository = electric_panels_repository

    def create_electric_panel(self, electric_panel_create: ElectricPanelCreate) -> ElectricPanel:
        return self.electric_panels_repository.create(electric_panel_create)

    def get_electric_panel_by_id(self, electric_panel_id: UUID) -> ElectricPanel | None:
        return self.electric_panels_repository.get(electric_panel_id)

    def get_electric_panel_by_attributes(self, name: str, location_id: UUID) -> ElectricPanel | None:
        electric_panels = self.electric_panels_repository.filter_by(name=name, location_id=location_id)
        if len(electric_panels) == 0:
            return None
        if len(electric_panels) > 1:
            raise ValueError('Multiple electric panels found with the same attributes')
        return electric_panels[0]

    def get_electric_panels_by_location(self, location_id: UUID) -> List[ElectricPanel]:
        return self.electric_panels_repository.filter_by(location_id=location_id)
    
    def filter_by(self, **kwargs) -> List[ElectricPanel]:
        return self.electric_panels_repository.filter_by(**kwargs)

    def delete_electric_panel(self, electric_panel_id: UUID) -> None:
        self.electric_panels_repository.delete(electric_panel_id)
