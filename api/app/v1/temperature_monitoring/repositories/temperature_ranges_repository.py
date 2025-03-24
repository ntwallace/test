from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.temperature_monitoring.models.temperature_range import TemperatureRange as TemperatureRangeModel
from app.v1.temperature_monitoring.schemas.temperature_range import TemperatureRange, TemperatureRangeCreate


class TemperatureRangesRepository(ABC):

    @abstractmethod
    def create(self, temperature_range_create: TemperatureRangeCreate) -> TemperatureRange:
        ...
    
    @abstractmethod
    def get(self, temperature_range_id: UUID) -> Optional[TemperatureRange]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[TemperatureRange]:
        ...
    
    @abstractmethod
    def delete(self, temperature_range_id: UUID) -> None:
        ...


class PostgresTemperatureRangesRepository(TemperatureRangesRepository):

    def __init__(self, session: Session):
        self.session = session

    @final
    def create(self, temperature_range_create: TemperatureRangeCreate) -> TemperatureRange:
        temperature_range = TemperatureRangeModel(
            high_degrees_celcius=temperature_range_create.high_degrees_celcius,
            low_degrees_celcius=temperature_range_create.low_degrees_celcius,
            warning_level=temperature_range_create.warning_level,
            temperature_sensor_place_id=temperature_range_create.temperature_sensor_place_id
        )
        self.session.add(temperature_range)
        self.session.commit()
        self.session.refresh(temperature_range)
        return TemperatureRange.model_validate(temperature_range, from_attributes=True)

    @final
    def get(self, temperature_range_id: UUID) -> Optional[TemperatureRange]:
        temperature_range = self.session.query(TemperatureRangeModel).filter(TemperatureRangeModel.temperature_range_id == temperature_range_id).first()
        if temperature_range is None:
            return None
        return TemperatureRange.model_validate(temperature_range, from_attributes=True)

    @final
    def filter_by(self, **kwargs) -> List[TemperatureRange]:
        temperature_ranges = self.session.query(TemperatureRangeModel).filter_by(**kwargs).all()
        return [
            TemperatureRange.model_validate(temperature_range, from_attributes=True)
            for temperature_range in temperature_ranges
        ]

    @final
    def delete(self, temperature_range_id: UUID) -> None:
        temperature_range = self.session.query(TemperatureRangeModel).filter(TemperatureRangeModel.temperature_range_id == temperature_range_id).first()
        if temperature_range:
            self.session.delete(temperature_range)
            self.session.commit()
