from typing import List, Optional
from uuid import UUID

from app.v1.temperature_monitoring.repositories.temperature_sensors_repository import TemperatureSensorsRepository
from app.v1.temperature_monitoring.schemas.temperature_sensor import TemperatureSensor, TemperatureSensorCreate


class TemperatureSensorsService:

    def __init__(self, temperature_sensors_repository: TemperatureSensorsRepository):
        self.temperature_sensors_repository = temperature_sensors_repository

    def create_temperature_sensor(self, temperature_sensor_create: TemperatureSensorCreate) -> TemperatureSensor:
        return self.temperature_sensors_repository.create(temperature_sensor_create)
    
    def get_temperature_sensors_by_location_id(self, location_id: UUID) -> List[TemperatureSensor]:
        return self.temperature_sensors_repository.filter_by(location_id=location_id)
    
    def get_temperature_sensor_by_id(self, temperature_sensor_id: UUID) -> Optional[TemperatureSensor]:
        return self.temperature_sensors_repository.get(temperature_sensor_id)
    
    def filter_by(self, **kwargs) -> List[TemperatureSensor]:
        return self.temperature_sensors_repository.filter_by(**kwargs)

    def delete_temperature_sensor(self, temperature_sensor_id: UUID) -> None:
        self.temperature_sensors_repository.delete(temperature_sensor_id)
