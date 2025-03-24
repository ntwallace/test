from typing import List, Optional
from uuid import UUID

from app.v1.temperature_monitoring.repositories.temperature_sensor_places_repository import TemperatureSensorPlacesRepository
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import TemperatureSensorPlace, TemperatureSensorPlaceCreate


class TemperatureSensorPlacesService:

    def __init__(self, temperature_sensor_places_repository: TemperatureSensorPlacesRepository):
        self.temperature_sensor_places_repository = temperature_sensor_places_repository

    def create_temperature_sensor_place(self, temperature_sensor_place_create: TemperatureSensorPlaceCreate) -> TemperatureSensorPlace:
        return self.temperature_sensor_places_repository.create(temperature_sensor_place_create)

    def get_temperature_sensor_places_for_location(self, location_id: UUID) -> List[TemperatureSensorPlace]:
        return self.temperature_sensor_places_repository.filter_by(location_id=location_id)

    def get_temperature_sensor_place(self, temperature_sensor_place_id: UUID) -> Optional[TemperatureSensorPlace]:
        return self.temperature_sensor_places_repository.get(temperature_sensor_place_id)

    def delete_temperature_sensor_place(self, temperature_sensor_place_id: UUID) -> None:
        self.temperature_sensor_places_repository.delete(temperature_sensor_place_id)

    def get_temperature_sensor_place_for_temperature_sensor(self, temperature_sensor_id: UUID) -> Optional[TemperatureSensorPlace]:
        temperature_sensor_places = self.temperature_sensor_places_repository.filter_by(temperature_sensor_id=temperature_sensor_id)
        if len(temperature_sensor_places) == 0:
            return None
        if len(temperature_sensor_places) > 1:
            raise ValueError(f"Multiple temperature sensor places found for temperature sensor {temperature_sensor_id}")
        return temperature_sensor_places[0]
    
    def filter_by(self, **kwargs) -> List[TemperatureSensorPlace]:
        return self.temperature_sensor_places_repository.filter_by(**kwargs)

    def get_temperature_sensor_places(self, temperature_sensor_place_ids: List[UUID]) -> List[TemperatureSensorPlace]:
        return self.temperature_sensor_places_repository.filter_by_temperature_sensor_place_ids(temperature_sensor_place_ids)
    
    def update_temperature_sensor_id(self, temperature_sensor_place_id: UUID, temperature_sensor_id: Optional[UUID]) -> Optional[TemperatureSensorPlace]:
        return self.temperature_sensor_places_repository.update(temperature_sensor_place_id, temperature_sensor_id=temperature_sensor_id)
