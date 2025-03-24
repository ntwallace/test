from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.electricity_dashboards.models.panel_system_health_electric_widget import PanelSystemHealthElectricWidget as PanelSystemHealthElectricWidgetModel
from app.v1.electricity_dashboards.schemas.panel_system_health_electric_widget import PanelSystemHealthElectricWidget, PanelSystemHealthElectricWidgetCreate


class PanelSystemHealthElectricWidgetsRepository(ABC):

    @abstractmethod
    def create(self, panel_system_health_electric_widget_create: PanelSystemHealthElectricWidgetCreate) -> PanelSystemHealthElectricWidget:
        pass

    @abstractmethod
    def get(self, electric_widget_id: UUID) -> Optional[PanelSystemHealthElectricWidget]:
        pass
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[PanelSystemHealthElectricWidget]:
        pass


class PostgresPanelSystemHealthElectricWidgetsRepository(PanelSystemHealthElectricWidgetsRepository):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    @final
    def create(self, panel_system_health_electric_widget_create: PanelSystemHealthElectricWidgetCreate) -> PanelSystemHealthElectricWidget:
        widget = PanelSystemHealthElectricWidgetModel(
            name=panel_system_health_electric_widget_create.name,
            electric_dashboard_id=panel_system_health_electric_widget_create.electric_dashboard_id
        )
        self.db_session.add(widget)
        self.db_session.commit()
        self.db_session.refresh(widget)
        return PanelSystemHealthElectricWidget.model_validate(widget, from_attributes=True)

    @final
    def get(self, electric_widget_id: UUID) -> Optional[PanelSystemHealthElectricWidget]:
        widget = self.db_session.query(PanelSystemHealthElectricWidgetModel).filter(PanelSystemHealthElectricWidgetModel.electric_widget_id == electric_widget_id).first()
        if widget is None:
            return None
        return PanelSystemHealthElectricWidget.model_validate(widget, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[PanelSystemHealthElectricWidget]:
        widgets = self.db_session.query(PanelSystemHealthElectricWidgetModel).filter_by(**kwargs).all()
        return [
            PanelSystemHealthElectricWidget.model_validate(widget, from_attributes=True)
            for widget in widgets
        ]
