from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.hvac.models.hvac_zone_temperature_sensor import HvacZoneTemperatureSensors as HvacZoneTemperatureSensorsModel
from app.v1.hvac.schemas.hvac_zone_temperature_sensor import HvacZoneTemperatureSensor, HvacZoneTemperatureSensorCreate


class HvacZoneTemperatureSensorsRepository(ABC):

    @abstractmethod
    def create(self, hvac_zone_temperature_sensor_create: HvacZoneTemperatureSensorCreate) -> HvacZoneTemperatureSensor:
        pass

    @abstractmethod
    def get(self, hvac_zone_temperature_sensor_id: UUID) -> Optional[HvacZoneTemperatureSensor]:
        pass

    @abstractmethod
    def filter_by(self, **kwargs) -> List[HvacZoneTemperatureSensor]:
        pass

    @abstractmethod
    def delete(self, hvac_zone_temperature_sensor_id: UUID) -> None:
       pass


class PostgresHvacZoneTemperatureSensorsRepository(HvacZoneTemperatureSensorsRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, hvac_zone_temperature_sensor_create: HvacZoneTemperatureSensorCreate) -> HvacZoneTemperatureSensor:
        hvac_zone_temperature_sensor = HvacZoneTemperatureSensorsModel(
            hvac_zone_id=hvac_zone_temperature_sensor_create.hvac_zone_id,
            temperature_sensor_id=hvac_zone_temperature_sensor_create.temperature_sensor_id
        )
        self.session.add(hvac_zone_temperature_sensor)
        self.session.commit()
        self.session.refresh(hvac_zone_temperature_sensor)
        return HvacZoneTemperatureSensor.model_validate(hvac_zone_temperature_sensor, from_attributes=True)

    @final
    def get(self, hvac_zone_temperature_sensor_id: UUID) -> Optional[HvacZoneTemperatureSensor]:
        hvac_zone_temperature_sensor = self.session.query(HvacZoneTemperatureSensorsModel).filter(HvacZoneTemperatureSensorsModel.hvac_zone_temperature_sensor_id == hvac_zone_temperature_sensor_id).first()
        if hvac_zone_temperature_sensor is None:
            return None
        return HvacZoneTemperatureSensor.model_validate(hvac_zone_temperature_sensor, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[HvacZoneTemperatureSensor]:
        hvac_zone_temperature_sensors = self.session.query(HvacZoneTemperatureSensorsModel).filter_by(**kwargs).all()
        return [
            HvacZoneTemperatureSensor.model_validate(hvac_zone_temperature_sensor, from_attributes=True)
            for hvac_zone_temperature_sensor in hvac_zone_temperature_sensors
        ]
    
    @final
    def delete(self, hvac_zone_temperature_sensor_id: UUID) -> None:
        hvac_zone_temperature_sensor = self.session.query(HvacZoneTemperatureSensorsModel).filter(HvacZoneTemperatureSensorsModel.hvac_zone_temperature_sensor_id == hvac_zone_temperature_sensor_id).first()
        if hvac_zone_temperature_sensor is not None:
            self.session.delete(hvac_zone_temperature_sensor)
            self.session.commit()
