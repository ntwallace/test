from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.temperature_dashboards.models.temeprature_unit_widget import TemperatureUnitWidget as TemperatureUnitWidgetModel
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import TemperatureUnitWidget, TemperatureUnitWidgetCreate, TemperatureUnitWidgetUpdate


class TemperatureUnitWidgetsRepository(ABC):

    @abstractmethod
    def create(self, temperature_unit_widget_create: TemperatureUnitWidgetCreate) -> TemperatureUnitWidget:
        raise NotImplementedError
    
    @abstractmethod
    def get(self, temperature_unit_widget_id: UUID) -> Optional[TemperatureUnitWidget]:
        raise NotImplementedError
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[TemperatureUnitWidget]:
        raise NotImplementedError
    
    @abstractmethod
    def update(self, temperature_unit_widget_id: UUID, temperature_unit_widget_update: TemperatureUnitWidgetUpdate) -> Optional[TemperatureUnitWidget]:
        raise NotImplementedError
    
    @abstractmethod
    def delete(self, temperature_unit_widget_id: UUID) -> None:
        raise NotImplementedError


class PostgresTemperatureUnitWidgetsRepository(TemperatureUnitWidgetsRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, temperature_unit_widget_create: TemperatureUnitWidgetCreate) -> TemperatureUnitWidget:
        try:
            temperature_unit_widget = TemperatureUnitWidgetModel(
                name=temperature_unit_widget_create.name,
                low_c=temperature_unit_widget_create.low_c,
                high_c=temperature_unit_widget_create.high_c,
                alert_threshold_s=temperature_unit_widget_create.alert_threshold_s,
                appliance_type=temperature_unit_widget_create.appliance_type,
                temperature_sensor_place_id=temperature_unit_widget_create.temperature_sensor_place_id,
                temperature_dashboard_id=temperature_unit_widget_create.temperature_dashboard_id
            )
            self.session.add(temperature_unit_widget)
            self.session.commit()
            self.session.refresh(temperature_unit_widget)
            return TemperatureUnitWidget.model_validate(temperature_unit_widget, from_attributes=True)
        except IntegrityError:
            raise ValueError

    @final
    def get(self, temperature_unit_widget_id: UUID) -> Optional[TemperatureUnitWidget]:
        temperature_unit_widget = self.session.query(TemperatureUnitWidgetModel).filter(TemperatureUnitWidgetModel.temperature_unit_widget_id == temperature_unit_widget_id).first()
        if temperature_unit_widget is None:
            return None
        return TemperatureUnitWidget.model_validate(temperature_unit_widget, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[TemperatureUnitWidget]:
        temperature_unit_widgets = self.session.query(TemperatureUnitWidgetModel).filter_by(**kwargs).all()
        return [
            TemperatureUnitWidget.model_validate(temperature_unit_widget, from_attributes=True)
            for temperature_unit_widget in temperature_unit_widgets
        ]
    
    @final
    def update(self, temperature_unit_widget_id: UUID, temperature_unit_widget_update: TemperatureUnitWidgetUpdate) -> Optional[TemperatureUnitWidget]:
        temperature_unit_widget = self.session.query(TemperatureUnitWidgetModel).filter(TemperatureUnitWidgetModel.temperature_unit_widget_id == temperature_unit_widget_id).first()
        if temperature_unit_widget is None:
            return None
        temperature_unit_widget.name = temperature_unit_widget_update.name
        temperature_unit_widget.low_c = temperature_unit_widget_update.low_c
        temperature_unit_widget.high_c = temperature_unit_widget_update.high_c
        temperature_unit_widget.alert_threshold_s = temperature_unit_widget_update.alert_threshold_s
        temperature_unit_widget.appliance_type = temperature_unit_widget_update.appliance_type
        self.session.commit()
        self.session.refresh(temperature_unit_widget)
        return TemperatureUnitWidget.model_validate(temperature_unit_widget, from_attributes=True)

    @final
    def delete(self, temperature_unit_widget_id: UUID) -> None:
        self.session.query(TemperatureUnitWidgetModel).filter(TemperatureUnitWidgetModel.temperature_unit_widget_id == temperature_unit_widget_id).delete()
        self.session.commit()
