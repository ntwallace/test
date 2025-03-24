from typing import List
from uuid import UUID

from app.v1.electricity_monitoring.repositories.electric_sensors_repository import ElectricSensorsRepository
from app.v1.electricity_monitoring.schemas.electric_sensor import ElectricSensor, ElectricSensorCreate


class ElectricSensorsService:

    def __init__(self, electric_sensors_repository: ElectricSensorsRepository):
        self.electric_sensors_repository = electric_sensors_repository

    def create_electric_sensor(self, electric_sensor_create: ElectricSensorCreate) -> ElectricSensor:
        return self.electric_sensors_repository.create(electric_sensor_create)

    def get_electric_sensor_by_id(self, electric_sensor_id: UUID) -> ElectricSensor | None:
        return self.electric_sensors_repository.get(electric_sensor_id)
        
    def get_electric_sensor_by_attributes(self, name: str, gateway_id: UUID, electric_panel_id: UUID) -> ElectricSensor | None:
        electric_sensors = self.electric_sensors_repository.filter_by(name=name, gateway_id=gateway_id, electric_panel_id=electric_panel_id)
        if len(electric_sensors) == 0:
            return None
        if len(electric_sensors) > 1:
            raise ValueError('Multiple electric sensors found with the same name, gateway_id and electric_panel_id')
        return electric_sensors[0]

    def get_electric_sensors_by_gateway(self, gateway_id: UUID) -> List[ElectricSensor]:
        return self.electric_sensors_repository.filter_by(gateway_id=gateway_id)
    
    def filter_by(self, **kwargs) -> List[ElectricSensor]:
        return self.electric_sensors_repository.filter_by(**kwargs)

    def delete_electric_sensor(self, electric_sensor_id: UUID) -> None:
        self.electric_sensors_repository.delete(electric_sensor_id)
