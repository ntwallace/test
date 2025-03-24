from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.electricity_monitoring.models.circuit import Circuit as CircuitModel
from app.v1.electricity_monitoring.schemas.circuit import Circuit, CircuitCreate, CircuitUpdate


class CircuitsRepository(ABC):

    @abstractmethod
    def create(self, circuit_create: CircuitCreate) -> Circuit:
        ...

    @abstractmethod
    def get(self, circuit_id: UUID) -> Optional[Circuit]:
        ...

    @abstractmethod
    def filter_by(self, **kwargs) -> List[Circuit]:
        ...
    
    @abstractmethod
    def update(self, circuit_update: CircuitUpdate) -> Optional[Circuit]:
        ...
    
    @abstractmethod
    def delete(self, circuit_id: UUID) -> None:
        ...


class PostgresCircuitsRepository(CircuitsRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, circuit_create: CircuitCreate) -> Circuit:
        try:
            circuit = CircuitModel(
                name=circuit_create.name,
                electric_panel_id=circuit_create.electric_panel_id,
                type=circuit_create.type,
            )
            self.session.add(circuit)
            self.session.commit()
            self.session.refresh(circuit)
            return Circuit.model_validate(circuit, from_attributes=True)
        except IntegrityError:
            raise ValueError('Circuit already exists')
    
    @final
    def get(self, circuit_id: UUID) -> Optional[Circuit]:
        circuit = self.session.query(CircuitModel).filter(CircuitModel.circuit_id == circuit_id).first()
        if circuit is None:
            return None
        return Circuit.model_validate(circuit, from_attributes=True)

    @final
    def filter_by(self, **kwargs) -> List[Circuit]:
        circuits = self.session.query(CircuitModel).filter_by(**kwargs).all()
        return [
            Circuit.model_validate(circuit, from_attributes=True)
            for circuit in circuits
        ]
    
    @final
    def update(self, circuit_update: CircuitUpdate) -> Optional[Circuit]:
        circuit = self.session.query(CircuitModel).filter(CircuitModel.circuit_id == circuit_update.circuit_id).first()
        if circuit is None:
            return None
        circuit.name = circuit_update.name
        self.session.commit()
        self.session.refresh(circuit)
        return Circuit.model_validate(circuit, from_attributes=True)
    
    @final
    def delete(self, circuit_id: UUID) -> None:
        circuit = self.session.query(CircuitModel).filter(CircuitModel.circuit_id == circuit_id).first()
        if circuit:
            self.session.delete(circuit)
            self.session.commit()
