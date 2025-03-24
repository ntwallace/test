from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.electricity_monitoring.models.electric_panel import ElectricPanel as ElectricPanelModel
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanel, ElectricPanelCreate


class ElectricPanelsRepository(ABC):

    @abstractmethod
    def create(self, electric_panel_create: ElectricPanelCreate) -> ElectricPanel:
        ...
    
    @abstractmethod
    def get(self, electric_panel_id: UUID) -> Optional[ElectricPanel]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[ElectricPanel]:
        ...
    
    @abstractmethod
    def delete(self, electric_panel_id: UUID) -> None:
        ...


class PostgresElectricPanelsRepository(ElectricPanelsRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, electric_panel_create: ElectricPanelCreate) -> ElectricPanel:
        try:
            electric_panel = ElectricPanelModel(
                name=electric_panel_create.name,
                panel_type=electric_panel_create.panel_type,
                location_id=electric_panel_create.location_id,
                breaker_count=electric_panel_create.breaker_count,
                parent_electric_panel_id=electric_panel_create.parent_electric_panel_id
            )
            self.session.add(electric_panel)
            self.session.commit()
            self.session.refresh(electric_panel)
            return ElectricPanel.model_validate(electric_panel, from_attributes=True)
        except IntegrityError:
            raise ValueError('Electric panel with the same attributes already exists')
    
    @final
    def get(self, electric_panel_id: UUID) -> Optional[ElectricPanel]:
        electric_panel = self.session.query(ElectricPanelModel).filter(ElectricPanelModel.electric_panel_id == electric_panel_id).first()
        if electric_panel is None:
            return None
        return ElectricPanel.model_validate(electric_panel, from_attributes=True)

    @final
    def filter_by(self, **kwargs) -> List[ElectricPanel]:
        electric_panels = self.session.query(ElectricPanelModel).filter_by(**kwargs).all()
        return [
            ElectricPanel.model_validate(electric_panel, from_attributes=True)
            for electric_panel in electric_panels
        ]
    
    @final
    def delete(self, electric_panel_id: UUID) -> None:
        electric_panel = self.session.query(ElectricPanelModel).filter(ElectricPanelModel.electric_panel_id == electric_panel_id).first()
        if electric_panel:
            self.session.delete(electric_panel)
            self.session.commit()
