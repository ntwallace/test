from typing import List, Optional
from uuid import UUID

from app.v1.temperature_monitoring.repositories.temperature_ranges_repository import TemperatureRangesRepository
from app.v1.temperature_monitoring.schemas.temperature_range import TemperatureRange, TemperatureRangeCreate


class TemperatureRangesService:

    def __init__(self, temperature_ranges_repository: TemperatureRangesRepository):
        self.temperature_ranges_repository = temperature_ranges_repository

    def create_temperature_range(self, temperature_range_create: TemperatureRangeCreate) -> TemperatureRange:
        return self.temperature_ranges_repository.create(temperature_range_create)

    def get_temperature_ranges_by_temperature_sensor_place_id(self, temperature_sensor_place_id: UUID) -> List[TemperatureRange]:
        return self.temperature_ranges_repository.filter_by(temperature_sensor_place_id=temperature_sensor_place_id)

    def get_temperature_range_by_id(self, temperature_range_id: UUID) -> Optional[TemperatureRange]:
        return self.temperature_ranges_repository.get(temperature_range_id)
    
    def get_temperature_range_for_temperature_sensor_place_by_id(self, temperature_sensor_place_id: UUID, temperature_range_id: UUID) -> Optional[TemperatureRange]:
        temperature_ranges = self.temperature_ranges_repository.filter_by(temperature_sensor_place_id=temperature_sensor_place_id, temperature_range_id=temperature_range_id)
        if len(temperature_ranges) == 0:
            return None
        if len(temperature_ranges) > 1:
            raise ValueError("Multiple temperature ranges found for temperature sensor place")
        return temperature_ranges[0]

    def delete_temperature_range_by_id(self, temperature_range_id: UUID) -> None:
        self.temperature_ranges_repository.delete(temperature_range_id)
