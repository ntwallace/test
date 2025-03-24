from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.hvac_dashboards.models.hvac_dashboard import HvacDashboard
from app.v1.hvac_dashboards.models.control_zone_hvac_widget import ControlZoneHvacWidget as ControlZoneHvacWidgetModel
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import ControlZoneHvacWidget, ControlZoneHvacWidgetCreate, ControlZoneHvacWidgetUpdate


class ControlZoneHvacWidgetsRepository(ABC):

    @abstractmethod
    def create(self, control_zone_hvac_widget_create: ControlZoneHvacWidgetCreate) -> ControlZoneHvacWidget:
        pass

    @abstractmethod
    def get_control_zone_hvac_widget(self, hvac_widget_id: UUID) -> Optional[ControlZoneHvacWidget]:
        pass

    @abstractmethod
    def update_control_zone_hvac_widget(self, hvac_widget_id: UUID, control_zone_hvac_widget_update: ControlZoneHvacWidgetUpdate) -> Optional[ControlZoneHvacWidget]:
        pass

    @abstractmethod
    def get_control_zone_hvac_widgets_with_schedule(self, schedule_id: UUID) -> List[ControlZoneHvacWidget]:
        pass

    @abstractmethod
    def get_control_zone_hvac_widgets_for_hvac_dashboard(self, hvac_dashboard_id: UUID) -> List[ControlZoneHvacWidget]:
        pass

    @abstractmethod
    def get_control_zone_hvac_widgets_for_location(self, location_id: UUID) -> List[ControlZoneHvacWidget]:
        pass

    @abstractmethod
    def filter_by(self, **kwargs) -> List[ControlZoneHvacWidget]:
        pass


class PostgresControlZoneHvacWidgetsRepository(ControlZoneHvacWidgetsRepository):

    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create(self, control_zone_hvac_widget_create: ControlZoneHvacWidgetCreate) -> ControlZoneHvacWidget:
        widget = ControlZoneHvacWidgetModel(
            name=control_zone_hvac_widget_create.name,
            hvac_zone_id=control_zone_hvac_widget_create.hvac_zone_id,
            hvac_dashboard_id=control_zone_hvac_widget_create.hvac_dashboard_id,
            monday_schedule_id=control_zone_hvac_widget_create.monday_schedule_id,
            tuesday_schedule_id=control_zone_hvac_widget_create.tuesday_schedule_id,
            wednesday_schedule_id=control_zone_hvac_widget_create.wednesday_schedule_id,
            thursday_schedule_id=control_zone_hvac_widget_create.thursday_schedule_id,
            friday_schedule_id=control_zone_hvac_widget_create.friday_schedule_id,
            saturday_schedule_id=control_zone_hvac_widget_create.saturday_schedule_id,
            sunday_schedule_id=control_zone_hvac_widget_create.sunday_schedule_id
        )
        try:
            self.db_session.add(widget)
            self.db_session.commit()
            self.db_session.refresh(widget)
            return ControlZoneHvacWidget.model_validate(widget, from_attributes=True)
        except IntegrityError:
            raise ValueError("Invalid HVAC widget data")

    def get_control_zone_hvac_widget(self, hvac_widget_id: UUID) -> Optional[ControlZoneHvacWidget]:
        widget = self.db_session.query(ControlZoneHvacWidgetModel).filter(ControlZoneHvacWidgetModel.hvac_widget_id == hvac_widget_id).first()
        if widget is None:
            return None
        return ControlZoneHvacWidget.model_validate(widget, from_attributes=True)
    
    def update_control_zone_hvac_widget(self, hvac_widget_id: UUID, control_zone_hvac_widget_update: ControlZoneHvacWidgetUpdate) -> ControlZoneHvacWidget | None:
        widget = self.db_session.query(ControlZoneHvacWidgetModel).filter(ControlZoneHvacWidgetModel.hvac_widget_id == hvac_widget_id).first()
        if widget is None:
            return None

        widget.name = control_zone_hvac_widget_update.name
        widget.monday_schedule_id = control_zone_hvac_widget_update.monday_schedule_id
        widget.tuesday_schedule_id = control_zone_hvac_widget_update.tuesday_schedule_id
        widget.wednesday_schedule_id = control_zone_hvac_widget_update.wednesday_schedule_id
        widget.thursday_schedule_id = control_zone_hvac_widget_update.thursday_schedule_id
        widget.friday_schedule_id = control_zone_hvac_widget_update.friday_schedule_id
        widget.saturday_schedule_id = control_zone_hvac_widget_update.saturday_schedule_id
        widget.sunday_schedule_id = control_zone_hvac_widget_update.sunday_schedule_id

        self.db_session.commit()
        self.db_session.refresh(widget)
        return ControlZoneHvacWidget.model_validate(widget, from_attributes=True)
    
    def get_control_zone_hvac_widgets_with_schedule(self, schedule_id: UUID) -> List[ControlZoneHvacWidget]:
        widgets = self.db_session.query(ControlZoneHvacWidgetModel).filter(
            (ControlZoneHvacWidgetModel.monday_schedule_id == schedule_id) |
            (ControlZoneHvacWidgetModel.tuesday_schedule_id == schedule_id) |
            (ControlZoneHvacWidgetModel.wednesday_schedule_id == schedule_id) |
            (ControlZoneHvacWidgetModel.thursday_schedule_id == schedule_id) |
            (ControlZoneHvacWidgetModel.friday_schedule_id == schedule_id) |
            (ControlZoneHvacWidgetModel.saturday_schedule_id == schedule_id) |
            (ControlZoneHvacWidgetModel.sunday_schedule_id == schedule_id)
        ).all()
        return [ControlZoneHvacWidget.model_validate(widget, from_attributes=True) for widget in widgets]

    def get_control_zone_hvac_widgets_for_hvac_dashboard(self, hvac_dashboard_id: UUID) -> List[ControlZoneHvacWidget]:
        widgets = self.db_session.query(ControlZoneHvacWidgetModel).filter(ControlZoneHvacWidgetModel.hvac_dashboard_id == hvac_dashboard_id).all()
        return [ControlZoneHvacWidget.model_validate(widget, from_attributes=True) for widget in widgets]
    
    def get_control_zone_hvac_widgets_for_location(self, location_id: UUID) -> List[ControlZoneHvacWidget]:
        widgets = (
            self.db_session.query(
                ControlZoneHvacWidgetModel
            ).join(
                HvacDashboard, HvacDashboard.hvac_dashboard_id == ControlZoneHvacWidgetModel.hvac_dashboard_id
            ).filter(
                HvacDashboard.location_id == location_id
            ).all()
        )
        return [ControlZoneHvacWidget.model_validate(widget, from_attributes=True) for widget in widgets]
    
    def filter_by(self, **kwargs) -> List[ControlZoneHvacWidget]:
        widgets = self.db_session.query(ControlZoneHvacWidgetModel).filter_by(**kwargs).all()
        return [
            ControlZoneHvacWidget.model_validate(widget, from_attributes=True)
            for widget in widgets
        ]
