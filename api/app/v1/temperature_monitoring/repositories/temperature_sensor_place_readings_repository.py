from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from app.v1.cache.cache import Cache
from app.v1.temperature_monitoring.schemas.temperature_sensor_place_reading import TemperatureSensorPlaceReading, TemperatureSensorPlaceReadingRaw


class TemperatureSensorPlaceReadingsRepository(ABC):

    @abstractmethod
    def get_latest_activity_for_temperature_sensor_place(self, temperature_sensor_place_id: UUID) -> Optional[TemperatureSensorPlaceReading]:
        pass


class CacheTemperatureSensorPlaceReadingsRepository(TemperatureSensorPlaceReadingsRepository):

    def __init__(self, cache: Cache):
        self._cache = cache
    
    def _temperature_places_activity_key(self, temperature_sensor_place_id: UUID) -> str:
        return f"temperature_place::{temperature_sensor_place_id!s}::activity"

    def get_latest_activity_for_temperature_sensor_place(self, temperature_sensor_place_id: UUID) -> Optional[TemperatureSensorPlaceReading]:
        cache_key = self._temperature_places_activity_key(temperature_sensor_place_id)
        response = self._cache.get(cache_key)
        if response is None:
            return None
        raw_activity = TemperatureSensorPlaceReadingRaw.model_validate_json(response)
        parsed_activity = TemperatureSensorPlaceReading(
            temperature_sensor_place_id=temperature_sensor_place_id,
            temperature_c=raw_activity.temperature_c,
            battery_percentage=raw_activity.battery_percentage,
            created_at=datetime.fromtimestamp(raw_activity.timestamp_ms_utc / 1000, tz=timezone.utc)
        )
        return parsed_activity
