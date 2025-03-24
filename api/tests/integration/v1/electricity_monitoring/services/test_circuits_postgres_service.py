from uuid import uuid4
import pytest
from sqlalchemy.orm import Session
from pydantic_core import ValidationError

from app.v1.electricity_monitoring.models.circuit import Circuit
from app.v1.electricity_monitoring.repositories.circuits_repository import PostgresCircuitsRepository
from app.v1.electricity_monitoring.repositories.electric_panels_repository import PostgresElectricPanelsRepository
from app.v1.electricity_monitoring.schemas.circuit import CircuitCreate
from app.v1.electricity_monitoring.services.circuits import CircuitsService


def test_create_circuit_inserts_new_model(db_session_for_tests: Session):
    service = CircuitsService(
        circuits_repository=PostgresCircuitsRepository(db_session_for_tests),
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    circuit_create = CircuitCreate(
        name="Test Circuit",
        electric_panel_id=uuid4(),
        type="main",
        circuit_id=uuid4()
    )
    circuits = service.create_circuit(circuit_create)
    circuits_model = db_session_for_tests.query(Circuit).all()
    assert len(circuits_model) == 1
    circuit_model = circuits_model[0]
    assert circuit_model.circuit_id == circuits.circuit_id
    assert circuit_model.name == circuits.name
    assert circuit_model.electric_panel_id == circuits.electric_panel_id
    assert circuit_model.type == circuits.type
    assert circuit_model.created_at == circuits.created_at
    assert circuit_model.updated_at == circuits.updated_at


def test_create_circuit_raises_error_if_circuit_exists(db_session_for_tests: Session):
    service = CircuitsService(
        circuits_repository=PostgresCircuitsRepository(db_session_for_tests),
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    circuit_create = CircuitCreate(
        name="Test Circuit",
        electric_panel_id=uuid4(),
        type="main",
        circuit_id=uuid4()
    )
    service.create_circuit(circuit_create)
    with pytest.raises(ValueError):
        service.create_circuit(circuit_create)


def test_create_circuit_raises_error_if_wrong_enum(db_session_for_tests: Session):
    with pytest.raises(ValidationError):
        circuit_create = CircuitCreate(
            name="Test Circuit",
            electric_panel_id=uuid4(),
            type="wrong",
            circuit_id=uuid4()
        )


def test_get_circuit_by_id_returns_correct_circuit(db_session_for_tests: Session):
    service = CircuitsService(
        circuits_repository=PostgresCircuitsRepository(db_session_for_tests),
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    circuit_create = CircuitCreate(
        name="Test Circuit",
        electric_panel_id=uuid4(),
        type="main",
        circuit_id=uuid4()
    )
    circuit = service.create_circuit(circuit_create)
    circuit_model = service.get_circuit_by_id(circuit.circuit_id)
    assert circuit_model.circuit_id == circuit.circuit_id
    assert circuit_model.name == circuit.name
    assert circuit_model.electric_panel_id == circuit.electric_panel_id
    assert circuit_model.type == circuit.type
    assert circuit_model.created_at == circuit.created_at
    assert circuit_model.updated_at == circuit.updated_at


def test_get_circuit_by_id_returns_none_if_circuit_does_not_exist(db_session_for_tests: Session):
    service = CircuitsService(
        circuits_repository=PostgresCircuitsRepository(db_session_for_tests),
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    circuit_model = service.get_circuit_by_id(uuid4())
    assert circuit_model is None


def test_get_circuit_by_attributes_returns_correct_circuit(db_session_for_tests: Session):
    service = CircuitsService(
        circuits_repository=PostgresCircuitsRepository(db_session_for_tests),
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    electric_panel_id = uuid4()
    circuit_create = CircuitCreate(
        name="Test Circuit",
        electric_panel_id=electric_panel_id,
        type="main",
        circuit_id=uuid4()
    )
    circuit = service.create_circuit(circuit_create)
    circuit_model = service.get_circuit_by_attributes(
        name=circuit.name,
        electric_panel_id=electric_panel_id,
        type=circuit.type
    )
    assert circuit_model.circuit_id == circuit.circuit_id
    assert circuit_model.name == circuit.name
    assert circuit_model.electric_panel_id == circuit.electric_panel_id
    assert circuit_model.type == circuit.type
    assert circuit_model.created_at == circuit.created_at
    assert circuit_model.updated_at == circuit.updated_at


def test_get_circuit_by_attributes_returns_none_if_circuit_does_not_exist(db_session_for_tests: Session):
    service = CircuitsService(
        circuits_repository=PostgresCircuitsRepository(db_session_for_tests),
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    circuit_model = service.get_circuit_by_attributes(
        name="Test Circuit",
        electric_panel_id=uuid4(),
        type="main"
    )
    assert circuit_model is None


def test_get_circuits_by_electric_panel_returns_correct_circuits(db_session_for_tests: Session):
    service = CircuitsService(
        circuits_repository=PostgresCircuitsRepository(db_session_for_tests),
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    electric_panel_id = uuid4()
    circuit_create = CircuitCreate(
        name="Test Circuit",
        electric_panel_id=electric_panel_id,
        type="main",
        circuit_id=uuid4()
    )
    circuit = service.create_circuit(circuit_create)
    circuits = service.get_circuits_by_electric_panel(electric_panel_id)
    assert len(circuits) == 1
    circuit_model = circuits[0]
    assert circuit_model.circuit_id == circuit.circuit_id
    assert circuit_model.name == circuit.name
    assert circuit_model.electric_panel_id == circuit.electric_panel_id
    assert circuit_model.type == circuit.type
    assert circuit_model.created_at == circuit.created_at
    assert circuit_model.updated_at == circuit.updated_at


def test_delete_circuit_deletes_correct_circuit(db_session_for_tests: Session):
    service = CircuitsService(
        circuits_repository=PostgresCircuitsRepository(db_session_for_tests),
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    circuit_create = CircuitCreate(
        name="Test Circuit",
        electric_panel_id=uuid4(),
        type="main",
        circuit_id=uuid4()
    )
    circuit = service.create_circuit(circuit_create)
    service.delete_circuit(circuit.circuit_id)
    circuit_model = service.get_circuit_by_id(circuit.circuit_id)
    assert circuit_model is None
