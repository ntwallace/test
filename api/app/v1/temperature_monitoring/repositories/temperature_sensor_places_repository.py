from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.temperature_monitoring.models.temperature_sensor_place import TemperatureSensorPlace as TemperatureSensorPlaceModel
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import TemperatureSensorPlace, TemperatureSensorPlaceCreate


class TemperatureSensorPlacesRepository(ABC):

    @abstractmethod
    def create(self, temperature_sensor_place_create: TemperatureSensorPlaceCreate) -> TemperatureSensorPlace:
        ...

    @abstractmethod
    def get(self, temperature_sensor_place_id: UUID) -> Optional[TemperatureSensorPlace]:
        ...

    @abstractmethod
    def filter_by(self, **kwargs) -> List[TemperatureSensorPlace]:
        ...

    @abstractmethod
    def filter_by_temperature_sensor_place_ids(self, temperature_sensor_place_ids: List[UUID]) -> List[TemperatureSensorPlace]:
        ...

    @abstractmethod
    def delete(self, temperature_sensor_place_id: UUID) -> None:
        ...
    
    @abstractmethod
    def update(self, temperature_sensor_place_id: UUID, **kwargs) -> Optional[TemperatureSensorPlace]:
        ...


class PostgresTemperatureSensorPlacesRepository(TemperatureSensorPlacesRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, temperature_sensor_place_create: TemperatureSensorPlaceCreate) -> TemperatureSensorPlace:
        temperature_sensor_place = TemperatureSensorPlaceModel(
            name=temperature_sensor_place_create.name,
            temperature_sensor_place_type=temperature_sensor_place_create.temperature_sensor_place_type,
            location_id=temperature_sensor_place_create.location_id,
            temperature_sensor_id=temperature_sensor_place_create.temperature_sensor_id
        )
        self.session.add(temperature_sensor_place)
        self.session.commit()
        self.session.refresh(temperature_sensor_place)
        return TemperatureSensorPlace.model_validate(temperature_sensor_place, from_attributes=True)

    @final
    def get(self, temperature_sensor_place_id: UUID) -> Optional[TemperatureSensorPlace]:
        temperature_sensor_place = self.session.query(TemperatureSensorPlaceModel).filter(TemperatureSensorPlaceModel.temperature_sensor_place_id == temperature_sensor_place_id).first()
        if temperature_sensor_place is None:
            return None
        return TemperatureSensorPlace.model_validate(temperature_sensor_place, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[TemperatureSensorPlace]:
        temperature_sensor_places = self.session.query(TemperatureSensorPlaceModel).filter_by(**kwargs).all()
        return [
            TemperatureSensorPlace.model_validate(temperature_sensor_place, from_attributes=True)
            for temperature_sensor_place in temperature_sensor_places
        ]
    
    @final
    def filter_by_temperature_sensor_place_ids(self, temperature_sensor_place_ids: List[UUID]) -> List[TemperatureSensorPlace]:
        temperature_sensor_places = self.session.query(TemperatureSensorPlaceModel).filter(TemperatureSensorPlaceModel.temperature_sensor_place_id.in_(temperature_sensor_place_ids)).all()
        return [
            TemperatureSensorPlace.model_validate(temperature_sensor_place, from_attributes=True)
            for temperature_sensor_place in temperature_sensor_places
        ]
    
    @final
    def delete(self, temperature_sensor_place_id: UUID) -> None:
        temperature_sensor_place = self.session.query(TemperatureSensorPlaceModel).filter(TemperatureSensorPlaceModel.temperature_sensor_place_id == temperature_sensor_place_id).first()
        if temperature_sensor_place:
            self.session.delete(temperature_sensor_place)
            self.session.commit()

    @final
    def update(self, temperature_sensor_place_id: UUID, **kwargs) -> Optional[TemperatureSensorPlace]:
        temperature_sensor_place = self.session.query(TemperatureSensorPlaceModel).filter(TemperatureSensorPlaceModel.temperature_sensor_place_id == temperature_sensor_place_id).first()
        if temperature_sensor_place is None:
            return None
        for key, value in kwargs.items():
            setattr(temperature_sensor_place, key, value)
        self.session.commit()
        self.session.refresh(temperature_sensor_place)
        return TemperatureSensorPlace.model_validate(temperature_sensor_place, from_attributes=True)
