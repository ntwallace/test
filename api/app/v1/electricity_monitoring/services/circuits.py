from typing import List
from uuid import UUID

from app.errors import NotFoundError
from app.v1.electricity_monitoring.repositories.circuits_repository import CircuitsRepository
from app.v1.electricity_monitoring.repositories.electric_panels_repository import ElectricPanelsRepository
from app.v1.electricity_monitoring.schemas.circuit import Circuit, CircuitCreate, CircuitTypeEnum, CircuitUpdate

class CircuitsService:

    def __init__(self,
                 circuits_repository: CircuitsRepository,
                 electric_panels_repository: ElectricPanelsRepository):
        self.circuits_repository = circuits_repository
        self.electric_panels_repository = electric_panels_repository

    def create_circuit(self, circuit_create: CircuitCreate) -> Circuit:
        return self.circuits_repository.create(circuit_create)

    def get_circuit_by_id(self, circuit_id: UUID) -> Circuit | None:
        return self.circuits_repository.get(circuit_id)

    def get_circuit_by_attributes(self, name: str, electric_panel_id: UUID, type: CircuitTypeEnum) -> Circuit | None:
        circuits = self.circuits_repository.filter_by(name=name, electric_panel_id=electric_panel_id, type=type)
        if len(circuits) == 0:
            return None
        if len(circuits) > 1:
            raise ValueError('Multiple circuits found with the same attributes')
        return circuits[0]

    def get_circuits_by_electric_panel(self, electric_panel_id: UUID) -> List[Circuit]:
        return self.circuits_repository.filter_by(electric_panel_id=electric_panel_id)

    def delete_circuit(self, circuit_id: UUID) -> None:
        self.circuits_repository.delete(circuit_id)
    
    def get_circuits_for_location(self, location_id: UUID) -> List[Circuit]:
        electric_panels = self.electric_panels_repository.filter_by(location_id=location_id)
        circuits = []
        for electric_panel in electric_panels:
            electric_panel_circuits = self.circuits_repository.filter_by(electric_panel_id=electric_panel.electric_panel_id)
            circuits.extend(electric_panel_circuits)
        return [
            Circuit.model_validate(circuit, from_attributes=True)
            for circuit in circuits
        ]

    def get_circuits_of_type_for_location(self, location_id: UUID, type: CircuitTypeEnum) -> List[Circuit]:
        electric_panels = self.electric_panels_repository.filter_by(location_id=location_id)
        circuits = []
        for electric_panel in electric_panels:
            electric_panel_circuits = self.circuits_repository.filter_by(electric_panel_id=electric_panel.electric_panel_id, type=type)
            circuits.extend(electric_panel_circuits)
        return [
            Circuit.model_validate(circuit)
            for circuit in circuits
        ]

    def get_circuits_of_type_for_electric_panel(self, electric_panel_id: UUID, type: CircuitTypeEnum) -> List[Circuit]:
        circuits = self.circuits_repository.filter_by(electric_panel_id=electric_panel_id, type=type)
        return [
            Circuit.model_validate(circuit)
            for circuit in circuits
        ]
    
    def update_circuit(self, circuit_update: CircuitUpdate) -> Circuit:
        updated_circuit = self.circuits_repository.update(circuit_update)
        if updated_circuit is None:
            raise NotFoundError('Circuit not found')
        return updated_circuit
    
    def filter_by(self, **kwargs) -> List[Circuit]:
        return self.circuits_repository.filter_by(**kwargs)
