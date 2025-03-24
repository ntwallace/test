from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import List, Optional, final
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.v1.temperature_monitoring.models.temperature_sensor_place_alert import TemperatureSensorPlaceAlert as TemperatureSensorPlaceAlertModel
from app.v1.temperature_monitoring.schemas.temperature_sensor_place_alert import TemperatureSensorPlaceAlert, TemperatureSensorPlaceAlertCreate


class TemperatureSensorPlaceAlertsRepository(ABC):

    @abstractmethod
    def create(self, temperature_sensor_place_alert_create: TemperatureSensorPlaceAlertCreate) -> TemperatureSensorPlaceAlert:
        ...

    @abstractmethod
    def get(self, temperature_sensor_place_alert_id: UUID) -> Optional[TemperatureSensorPlaceAlert]:
        ...

    @abstractmethod
    def filter_by(self, **kwargs) -> List[TemperatureSensorPlaceAlert]:
        ...

    @abstractmethod
    def delete(self, temperature_sensor_place_alert_id: UUID) -> None:
        ...
    
    @abstractmethod
    def get_active_alerts_between_datetimes_for_temperature_sensor_places(self, temperature_sensor_place_ids: List[UUID], period_start: datetime, period_end: datetime, tz_string: str = 'UTC') -> List[TemperatureSensorPlaceAlert]:
        ...
    
    @abstractmethod
    def get_active_alerts_for_temperature_sensor_places(self, temperature_sensor_place_ids: List[UUID]) -> List[TemperatureSensorPlaceAlert]:
        ...


class PostgresTemperatureSensorPlaceAlertsRepository(TemperatureSensorPlaceAlertsRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, temperature_sensor_place_alert_create: TemperatureSensorPlaceAlertCreate) -> TemperatureSensorPlaceAlert:
        temperature_sensor_place_alert = TemperatureSensorPlaceAlertModel(
            temperature_sensor_place_id=temperature_sensor_place_alert_create.temperature_sensor_place_id,
            alert_type=temperature_sensor_place_alert_create.alert_type,
            threshold_temperature_c=temperature_sensor_place_alert_create.threshold_temperature_c,
            threshold_window_seconds=temperature_sensor_place_alert_create.threshold_window_seconds,
            reporter_temperature_c=temperature_sensor_place_alert_create.reporter_temperature_c,
            started_at=temperature_sensor_place_alert_create.started_at,
            ended_at=temperature_sensor_place_alert_create.ended_at
        )
        self.session.add(temperature_sensor_place_alert)
        self.session.commit()
        self.session.refresh(temperature_sensor_place_alert)
        return TemperatureSensorPlaceAlert.model_validate(temperature_sensor_place_alert, from_attributes=True)

    @final
    def get(self, temperature_sensor_place_alert_id: UUID) -> Optional[TemperatureSensorPlaceAlert]:
        temperature_sensor_place_alert = self.session.query(TemperatureSensorPlaceAlertModel).filter(TemperatureSensorPlaceAlertModel.temperature_sensor_place_alert_id == temperature_sensor_place_alert_id).first()
        if temperature_sensor_place_alert is None:
            return None
        return TemperatureSensorPlaceAlert.model_validate(temperature_sensor_place_alert, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[TemperatureSensorPlaceAlert]:
        temperature_sensor_place_alerts = self.session.query(TemperatureSensorPlaceAlertModel).filter_by(**kwargs).all()
        return [
            TemperatureSensorPlaceAlert.model_validate(temperature_sensor_place_alert, from_attributes=True)
            for temperature_sensor_place_alert in temperature_sensor_place_alerts
        ]
    
    @final
    def filter_by_temperature_sensor_place_alert_ids(self, temperature_sensor_place_alert_ids: List[UUID]) -> List[TemperatureSensorPlaceAlert]:
        temperature_sensor_place_alerts = self.session.query(TemperatureSensorPlaceAlertModel).filter(TemperatureSensorPlaceAlertModel.temperature_sensor_place_alert_id.in_(temperature_sensor_place_alert_ids)).all()
        return [
            TemperatureSensorPlaceAlert.model_validate(temperature_sensor_place_alert, from_attributes=True)
            for temperature_sensor_place_alert in temperature_sensor_place_alerts
        ]
    
    @final
    def delete(self, temperature_sensor_place_alert_id: UUID) -> None:
        temperature_sensor_place_alert = self.session.query(TemperatureSensorPlaceAlertModel).filter(TemperatureSensorPlaceAlertModel.temperature_sensor_place_alert_id == temperature_sensor_place_alert_id).first()
        if temperature_sensor_place_alert:
            self.session.delete(temperature_sensor_place_alert)
            self.session.commit()

    @final
    def get_active_alerts_between_datetimes_for_temperature_sensor_places(self, temperature_sensor_place_ids: List[UUID], period_start: datetime, period_end: datetime, tz_string: str = 'UTC') -> List[TemperatureSensorPlaceAlert]:
        tz_info = ZoneInfo(tz_string)
        period_start = period_start.replace(tzinfo=tz_info).astimezone(timezone.utc)
        period_end = period_end.replace(tzinfo=tz_info).astimezone(timezone.utc)
        temperature_sensor_place_alerts = (
            self.session.query(
                TemperatureSensorPlaceAlertModel
            )
            .filter(
                TemperatureSensorPlaceAlertModel.temperature_sensor_place_id.in_(temperature_sensor_place_ids),
                or_(
                    and_(
                        TemperatureSensorPlaceAlertModel.ended_at.is_(None),
                        TemperatureSensorPlaceAlertModel.started_at <= period_end,
                    ),
                    and_(
                        TemperatureSensorPlaceAlertModel.ended_at.isnot(None),
                        or_(
                            and_(
                                TemperatureSensorPlaceAlertModel.started_at >= period_start,
                                TemperatureSensorPlaceAlertModel.started_at <= period_end
                            ),
                            and_(
                                TemperatureSensorPlaceAlertModel.ended_at >= period_start,
                                TemperatureSensorPlaceAlertModel.ended_at <= period_end
                            )
                        )
                    )
                )
            )
        )
        return [
            TemperatureSensorPlaceAlert.model_validate(temperature_sensor_place_alert, from_attributes=True)
            for temperature_sensor_place_alert in temperature_sensor_place_alerts
        ]

    @final
    def get_active_alerts_for_temperature_sensor_places(self, temperature_sensor_place_ids: List[UUID]) -> List[TemperatureSensorPlaceAlert]:
        temperature_sensor_place_alerts = (
            self.session.query(
                TemperatureSensorPlaceAlertModel
            )
            .filter(
                TemperatureSensorPlaceAlertModel.temperature_sensor_place_id.in_(temperature_sensor_place_ids),
                TemperatureSensorPlaceAlertModel.ended_at.is_(None)
            )
        )
        return [
            TemperatureSensorPlaceAlert.model_validate(temperature_sensor_place_alert, from_attributes=True)
            for temperature_sensor_place_alert in temperature_sensor_place_alerts
        ]