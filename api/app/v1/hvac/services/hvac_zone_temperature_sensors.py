from typing import final
from uuid import UUID

from app.v1.hvac.repositories.hvac_zone_temperature_sensors_repository import HvacZoneTemperatureSensorsRepository
from app.v1.hvac.schemas.hvac_zone_temperature_sensor import HvacZoneTemperatureSensor, HvacZoneTemperatureSensorCreate


class HvacZoneTemperatureSensorsService:

    def __init__(self, hvac_zone_temperature_sensors_repository: HvacZoneTemperatureSensorsRepository):
        self.hvac_zone_temperature_sensors_repository = hvac_zone_temperature_sensors_repository

    def create_hvac_zone_temperature_sensor(self, hvac_zone_temperature_sensor_create: HvacZoneTemperatureSensorCreate) -> HvacZoneTemperatureSensor:
        return self.hvac_zone_temperature_sensors_repository.create(hvac_zone_temperature_sensor_create)
    
    def get_hvac_zone_temperature_sensor_by_id(self, hvac_zone_temperature_sensor_id: UUID) -> HvacZoneTemperatureSensor | None:
        return self.hvac_zone_temperature_sensors_repository.get(hvac_zone_temperature_sensor_id)

    def get_hvac_zone_temperature_sensor_by_attributes(self, hvac_zone_id: UUID, temperature_sensor_id: UUID) -> HvacZoneTemperatureSensor | None:
        hvac_zone_temperature_sensors = self.hvac_zone_temperature_sensors_repository.filter_by(hvac_zone_id=hvac_zone_id, temperature_sensor_id=temperature_sensor_id)
        if len(hvac_zone_temperature_sensors) == 0:
            return None
        if len(hvac_zone_temperature_sensors) > 1:
            raise ValueError('Multiple hvac zone temperature sensors found with the same attributes')
        return hvac_zone_temperature_sensors[0]

    def get_hvac_zone_temperature_sensors_by_hvac_zone_id(self, hvac_zone_id: UUID) -> list[HvacZoneTemperatureSensor]:
        return self.hvac_zone_temperature_sensors_repository.filter_by(hvac_zone_id=hvac_zone_id)

    @final
    def delete_hvac_zone_temperature_sensor(self, hvac_zone_temperature_sensor_id: UUID) -> None:
        self.hvac_zone_temperature_sensors_repository.delete(hvac_zone_temperature_sensor_id)
