from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.electricity_dashboards.models.energy_load_curve_electric_widget import EnergyLoadCurveElectricWidget as EnergyLoadCurveElectricWidgetModel
from app.v1.electricity_dashboards.schemas.energy_load_curve_electric_widget import EnergyLoadCurveElectricWidget, EnergyLoadCurveElectricWidgetCreate


class EnergyLoadCurveElectricWidgetsRepository(ABC):
    
    @abstractmethod
    def create(self, energy_load_curve_electric_widget_create: EnergyLoadCurveElectricWidgetCreate) -> EnergyLoadCurveElectricWidget:
        pass

    @abstractmethod
    def get(self, widget_id: UUID) -> Optional[EnergyLoadCurveElectricWidget]:
        pass

    @abstractmethod
    def filter_by(self, **kwargs) -> List[EnergyLoadCurveElectricWidget]:
        pass


class PostgresEnergyLoadCurveElectricWidgetsRepository(EnergyLoadCurveElectricWidgetsRepository):

    def __init__(self, db_session: Session):
        self._db_session = db_session
    
    @final
    def create(self, energy_load_curve_electric_widget_create: EnergyLoadCurveElectricWidgetCreate) -> EnergyLoadCurveElectricWidget:
        widget = EnergyLoadCurveElectricWidgetModel(
            name=energy_load_curve_electric_widget_create.name,
            electric_dashboard_id=energy_load_curve_electric_widget_create.electric_dashboard_id
        )
        self._db_session.add(widget)
        self._db_session.commit()
        self._db_session.refresh(widget)
        widget_schema = EnergyLoadCurveElectricWidget.model_validate(widget, from_attributes=True)
        return widget_schema

    @final
    def get(self, widget_id: UUID) -> Optional[EnergyLoadCurveElectricWidget]:
        widget = self._db_session.query(EnergyLoadCurveElectricWidgetModel).filter(EnergyLoadCurveElectricWidgetModel.electric_widget_id == widget_id).first()
        if widget is None:
            return None
        widget_schema = EnergyLoadCurveElectricWidget.model_validate(widget, from_attributes=True)
        return widget_schema
    
    @final
    def filter_by(self, **kwargs) -> List[EnergyLoadCurveElectricWidget]:
        widgets = self._db_session.query(EnergyLoadCurveElectricWidgetModel).filter_by(**kwargs).all()
        return [
            EnergyLoadCurveElectricWidget.model_validate(widget, from_attributes=True)
            for widget in widgets
        ]
