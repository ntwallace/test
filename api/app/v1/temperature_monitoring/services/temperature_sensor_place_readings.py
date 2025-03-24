from typing import Optional
from uuid import UUID

from app.v1.temperature_monitoring.repositories.temperature_sensor_place_readings_repository import TemperatureSensorPlaceReadingsRepository
from app.v1.temperature_monitoring.schemas.temperature_sensor_place_reading import TemperatureSensorPlaceReading


class TemperatureSensorPlaceReadingsService:

    def __init__(
        self,
        temperature_sensor_place_readings_repository: TemperatureSensorPlaceReadingsRepository
    ):
        self._temperature_sensor_place_readings_repository = temperature_sensor_place_readings_repository
    
    def get_latest_activity_for_temperature_sensor_place(self, temperature_sensor_place_id: UUID) -> Optional[TemperatureSensorPlaceReading]:
        return self._temperature_sensor_place_readings_repository.get_latest_activity_for_temperature_sensor_place(temperature_sensor_place_id)
