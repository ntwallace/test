from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.electricity_monitoring.models.clamp import Clamp as ClampModel
from app.v1.electricity_monitoring.schemas.clamp import Clamp, ClampCreate

class ClampsRepository(ABC):

    @abstractmethod
    def create(self, clamp_create: ClampCreate) -> Clamp:
        ...

    @abstractmethod
    def get(self, clamp_id: UUID) -> Optional[Clamp]:
        ...

    @abstractmethod
    def filter_by(self, **kwargs) -> List[Clamp]:
        ...
    
    @abstractmethod
    def delete(self, clamp_id: UUID) -> None:
        ...


class PostgresClampsRepository(ClampsRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, clamp_create: ClampCreate) -> Clamp:
        try:
            clamp = ClampModel(
                name=clamp_create.name,
                port_name=clamp_create.port_name,
                port_pin=clamp_create.port_pin,
                amperage_rating=clamp_create.amperage_rating,
                phase=clamp_create.phase,
                circuit_id=clamp_create.circuit_id,
                electric_sensor_id=clamp_create.electric_sensor_id,
            )
            self.session.add(clamp)
            self.session.commit()
            self.session.refresh(clamp)
            return Clamp.model_validate(clamp, from_attributes=True)
        except IntegrityError:
            raise ValueError('Clamp already exists')

    @final
    def get(self, clamp_id: UUID) -> Optional[Clamp]:
        clamp = self.session.query(ClampModel).filter(ClampModel.clamp_id == clamp_id).first()
        if clamp is None:
            return None
        return Clamp.model_validate(clamp, from_attributes=True)

    @final
    def filter_by(self, **kwargs) -> List[Clamp]:
        clamps = self.session.query(ClampModel).filter_by(**kwargs).all()
        return [
            Clamp.model_validate(clamp, from_attributes=True)
            for clamp in clamps
        ]
    
    @final
    def delete(self, clamp_id: UUID) -> None:
        clamp = self.session.query(ClampModel).filter(ClampModel.clamp_id == clamp_id).first()
        if clamp:
            self.session.delete(clamp)
            self.session.commit()
