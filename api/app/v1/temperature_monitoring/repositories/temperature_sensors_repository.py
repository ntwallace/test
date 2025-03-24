from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.temperature_monitoring.models.temperature_sensor import TemperatureSensor as TemperatureSensorModel
from app.v1.temperature_monitoring.schemas.temperature_sensor import TemperatureSensor, TemperatureSensorCreate


class TemperatureSensorsRepository(ABC):

    @abstractmethod
    def create(self, temperature_sensor_create: TemperatureSensorCreate) -> TemperatureSensor:
        ...
    
    @abstractmethod
    def get(self, temperature_sensor_id: UUID) -> Optional[TemperatureSensor]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[TemperatureSensor]:
        ...
    
    @abstractmethod
    def delete(self, temperature_sensor_id: UUID) -> None:
        ...


class PostgresTemperatureSensorsRepository(TemperatureSensorsRepository):

    def __init__(self, session: Session):
        self.session = session

    @final
    def create(self, temperature_sensor_create: TemperatureSensorCreate) -> TemperatureSensor:
        temperature_sensor = TemperatureSensorModel(
            name=temperature_sensor_create.name,
            duid=temperature_sensor_create.duid,
            make=temperature_sensor_create.make,
            model=temperature_sensor_create.model,
            gateway_id=temperature_sensor_create.gateway_id,
            location_id=temperature_sensor_create.location_id
        )
        self.session.add(temperature_sensor)
        self.session.commit()
        self.session.refresh(temperature_sensor)
        return TemperatureSensor.model_validate(temperature_sensor, from_attributes=True)

    @final
    def get(self, temperature_sensor_id: UUID) -> Optional[TemperatureSensor]:
        temperature_sensor = self.session.query(TemperatureSensorModel).filter(TemperatureSensorModel.temperature_sensor_id == temperature_sensor_id).first()
        if temperature_sensor is None:
            return None
        return TemperatureSensor.model_validate(temperature_sensor, from_attributes=True)

    @final
    def filter_by(self, **kwargs) -> List[TemperatureSensor]:
        temperature_sensors = self.session.query(TemperatureSensorModel).filter_by(**kwargs).all()
        return [
            TemperatureSensor.model_validate(temperature_sensor, from_attributes=True)
            for temperature_sensor in temperature_sensors
        ]

    @final
    def delete(self, temperature_sensor_id: UUID) -> None:
        temperature_sensor = self.session.query(TemperatureSensorModel).filter(TemperatureSensorModel.temperature_sensor_id == temperature_sensor_id).first()
        if temperature_sensor:
            self.session.delete(temperature_sensor)
            self.session.commit()
