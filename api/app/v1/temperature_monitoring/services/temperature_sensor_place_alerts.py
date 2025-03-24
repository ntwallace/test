from datetime import datetime, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo
from uuid import UUID

from app.v1.temperature_monitoring.repositories.temperature_sensor_place_alerts_repository import TemperatureSensorPlaceAlertsRepository
from app.v1.temperature_monitoring.repositories.temperature_sensor_places_repository import TemperatureSensorPlacesRepository
from app.v1.temperature_monitoring.schemas.temperature_sensor_place_alert import TemperatureSensorPlaceAlert, TemperatureSensorPlaceAlertCreate


class TemperatureSensorPlaceAlertsService:

    def __init__(
        self,
        temperature_sensor_place_alerts_repository: TemperatureSensorPlaceAlertsRepository,
        temperature_sensor_places_repository: TemperatureSensorPlacesRepository
    ):
        self.temperature_sensor_place_alerts_repository = temperature_sensor_place_alerts_repository
        self.temperature_sensor_places_repository = temperature_sensor_places_repository

    def create_temperature_sensor_place_alert(self, temperature_sensor_place_alert_create: TemperatureSensorPlaceAlertCreate) -> TemperatureSensorPlaceAlert:
        return self.temperature_sensor_place_alerts_repository.create(temperature_sensor_place_alert_create)

    def get_temperature_sensor_place_alerts_for_temperature_sensor_place(self, temperature_sensor_place_id: UUID) -> List[TemperatureSensorPlaceAlert]:
        return self.temperature_sensor_place_alerts_repository.filter_by(temperature_sensor_place_id=temperature_sensor_place_id)

    def get_temperature_sensor_place_alert_for_temperature_sensor_place(self, temperature_sensor_place_id: UUID, temperature_sensor_place_alert_id: UUID) -> Optional[TemperatureSensorPlaceAlert]:
        temperature_sensor_place_alerts = self.temperature_sensor_place_alerts_repository.filter_by(temperature_sensor_place_id=temperature_sensor_place_id, temperature_sensor_place_alert_id=temperature_sensor_place_alert_id)
        if len(temperature_sensor_place_alerts) == 0:
            return None
        if len(temperature_sensor_place_alerts) > 1:
            raise ValueError(f"Multiple temperature sensor place alerts found for temperature sensor place {temperature_sensor_place_id}")
        return temperature_sensor_place_alerts[0]

    def delete_temperature_sensor_place_alert(self, temperature_sensor_place_alert_id: UUID) -> None:
        self.temperature_sensor_place_alerts_repository.delete(temperature_sensor_place_alert_id)
    
    def get_temperature_sensor_place_alerts_for_location(self, location_id: UUID, period_start: datetime, period_end: datetime, tz_string: str = 'UTC') -> List[TemperatureSensorPlaceAlert]:
        tz_info = ZoneInfo(tz_string)
        period_start = period_start.replace(tzinfo=tz_info).astimezone(timezone.utc)
        period_end = period_end.replace(tzinfo=tz_info).astimezone(timezone.utc)

        temperature_sensor_places = self.temperature_sensor_places_repository.filter_by(location_id=location_id)
        temperature_sensor_place_ids = [temperature_sensor_place.temperature_sensor_place_id for temperature_sensor_place in temperature_sensor_places]

        return self.temperature_sensor_place_alerts_repository.get_active_alerts_between_datetimes_for_temperature_sensor_places(
            temperature_sensor_place_ids=temperature_sensor_place_ids,
            period_start=period_start,
            period_end=period_end,
            tz_string=tz_string
        )
        
    def get_active_temperature_sensor_place_alerts_for_location(self, location_id: UUID) -> List[TemperatureSensorPlaceAlert]:
        temperature_sensor_places = self.temperature_sensor_places_repository.filter_by(location_id=location_id)
        temperature_sensor_place_ids = [temperature_sensor_place.temperature_sensor_place_id for temperature_sensor_place in temperature_sensor_places]

        return self.temperature_sensor_place_alerts_repository.get_active_alerts_for_temperature_sensor_places(
            temperature_sensor_place_ids=temperature_sensor_place_ids
        )
