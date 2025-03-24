from typing import List
from uuid import UUID

from app.v1.electricity_monitoring.repositories.clamps_repository import ClampsRepository
from app.v1.electricity_monitoring.repositories.electric_sensors_repository import ElectricSensorsRepository
from app.v1.electricity_monitoring.schemas.clamp import Clamp, ClampCreate, ClampPhaseEnum


class ClampsService:

    def __init__(self,
                 clamps_repository: ClampsRepository,
                 electric_sensors_repository: ElectricSensorsRepository):
        self.clamps_repository = clamps_repository
        self.electric_sensors_repository = electric_sensors_repository

    def create_clamp(self, clamp_create: ClampCreate) -> Clamp:
        return self.clamps_repository.create(clamp_create)

    def get_clamp_by_id(self, clamp_id: UUID) -> Clamp | None:
        return self.clamps_repository.get(clamp_id)

    def get_clamp_by_attributes(self, name: str, circuit_id: UUID, phase: ClampPhaseEnum) -> Clamp | None:
        clamps = self.clamps_repository.filter_by(name=name, circuit_id=circuit_id, phase=phase)
        if len(clamps) == 0:
            return None
        if len(clamps) > 1:
            raise ValueError('Multiple clamps found with the same name, circuit_id and phase')
        return clamps[0]

    def get_clamps_by_circuit(self, circuit_id: UUID) -> List[Clamp]:
        return self.clamps_repository.filter_by(circuit_id=circuit_id)

    def delete_clamp(self, clamp_id: UUID) -> None:
        self.clamps_repository.delete(clamp_id)

    def get_clamps_for_gateway(self, gateway_id: UUID) -> List[Clamp]:
        electric_sensors = self.electric_sensors_repository.filter_by(gateway_id=gateway_id)
        clamps: List[Clamp] = []
        for electric_sensor in electric_sensors:
            electric_sensor_clamps = self.clamps_repository.filter_by(electric_sensor_id=electric_sensor.electric_sensor_id)
            clamps.extend(electric_sensor_clamps)
        return clamps

    def filter_by(self, **kwargs) -> List[Clamp]:
        return self.clamps_repository.filter_by(**kwargs)
