from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.electricity_dashboards.models.energy_consumption_breakdown_electric_widget import EnergyConsumptionBreakdownElectricWidget as EnergyConsumptionBreakdownElectricWidgetModel
from app.v1.electricity_dashboards.schemas.energy_consumption_breakdown_electric_widget import EnergyConsumptionBreakdownElectricWidget, EnergyConsumptionBreakdownElectricWidgetCreate


class EnergyConsumptionBreakdownElectricWidgetRepository(ABC):

    @abstractmethod
    def create(self, energy_consumption_breakdown_electric_widget_create: EnergyConsumptionBreakdownElectricWidgetCreate) -> EnergyConsumptionBreakdownElectricWidget:
        pass

    @abstractmethod
    def get(self, widget_id: UUID) -> Optional[EnergyConsumptionBreakdownElectricWidget]:
        pass

    @abstractmethod
    def filter_by(self, **kwargs) -> List[EnergyConsumptionBreakdownElectricWidget]:
        pass


class PostgresEnergyConsumptionBreakdownElectricWidgetRepository(EnergyConsumptionBreakdownElectricWidgetRepository):

    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    @final
    def create(self, energy_consumption_breakdown_electric_widget_create: EnergyConsumptionBreakdownElectricWidgetCreate) -> EnergyConsumptionBreakdownElectricWidget:
        widget = EnergyConsumptionBreakdownElectricWidgetModel(
            name=energy_consumption_breakdown_electric_widget_create.name,
            electric_dashboard_id=energy_consumption_breakdown_electric_widget_create.electric_dashboard_id
        )
        self.db_session.add(widget)
        self.db_session.commit()
        self.db_session.refresh(widget)
        return EnergyConsumptionBreakdownElectricWidget.model_validate(widget, from_attributes=True)

    @final
    def get(self, widget_id: UUID) -> Optional[EnergyConsumptionBreakdownElectricWidget]:
        widget = self.db_session.query(EnergyConsumptionBreakdownElectricWidgetModel).filter(EnergyConsumptionBreakdownElectricWidgetModel.electric_widget_id == widget_id).first()
        if widget is None:
            return None
        widget_schema = EnergyConsumptionBreakdownElectricWidget.model_validate(widget, from_attributes=True)
        return widget_schema        
    
    @final
    def filter_by(self, **kwargs) -> List[EnergyConsumptionBreakdownElectricWidget]:
        widgets = self.db_session.query(EnergyConsumptionBreakdownElectricWidgetModel).filter_by(**kwargs).all()
        return [
            EnergyConsumptionBreakdownElectricWidget.model_validate(widget, from_attributes=True)
            for widget in widgets
        ]
