from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.electricity_monitoring.models.electric_sensor import ElectricSensor as ElectricSensorModel
from app.v1.electricity_monitoring.schemas.electric_sensor import ElectricSensor, ElectricSensorCreate


class ElectricSensorsRepository(ABC):

    @abstractmethod
    def create(self, electric_sensor_create: ElectricSensorCreate) -> ElectricSensor:
        ...
    
    @abstractmethod
    def get(self, electric_sensor_id: UUID) -> Optional[ElectricSensor]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[ElectricSensor]:
        ...
    
    @abstractmethod
    def delete(self, electric_sensor_id: UUID) -> None:
        ...


class PostgresElectricSensorsRepository(ElectricSensorsRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, electric_sensor_create: ElectricSensorCreate) -> ElectricSensor:
        try:
            electric_sensor = ElectricSensorModel(
                name=electric_sensor_create.name,
                duid=electric_sensor_create.duid,
                port_count=electric_sensor_create.port_count,
                electric_panel_id=electric_sensor_create.electric_panel_id,
                gateway_id=electric_sensor_create.gateway_id,
                a_breaker_num=electric_sensor_create.a_breaker_num,
                b_breaker_num=electric_sensor_create.b_breaker_num,
                c_breaker_num=electric_sensor_create.c_breaker_num,
            )
            self.session.add(electric_sensor)
            self.session.commit()
            self.session.refresh(electric_sensor)
            return ElectricSensor.model_validate(electric_sensor, from_attributes=True)
        except IntegrityError:
            raise ValueError('Electric Sensor already exists')
    
    @final
    def get(self, electric_sensor_id: UUID) -> Optional[ElectricSensor]:
        electric_sensor = self.session.query(ElectricSensorModel).filter(ElectricSensorModel.electric_sensor_id == electric_sensor_id).first()
        if electric_sensor is None:
            return None
        return ElectricSensor.model_validate(electric_sensor, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[ElectricSensor]:
        electric_sensors = self.session.query(ElectricSensorModel).filter_by(**kwargs).all()
        return [
            ElectricSensor.model_validate(electric_sensor, from_attributes=True)
            for electric_sensor in electric_sensors   
        ]

    @final
    def delete(self, electric_sensor_id: UUID) -> None:
        electric_sensor = self.session.query(ElectricSensorModel).filter(ElectricSensorModel.electric_sensor_id == electric_sensor_id).first()
        if electric_sensor:
            self.session.delete(electric_sensor)
            self.session.commit()
