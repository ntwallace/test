from uuid import uuid4
import pytest
from sqlalchemy.orm import Session
from pydantic_core import ValidationError

from app.v1.electricity_monitoring.models.clamp import Clamp
from app.v1.electricity_monitoring.repositories.clamps_repository import PostgresClampsRepository
from app.v1.electricity_monitoring.repositories.electric_sensors_repository import PostgresElectricSensorsRepository
from app.v1.electricity_monitoring.schemas.clamp import ClampCreate
from app.v1.electricity_monitoring.services.clamps import ClampsService


def test_create_clamp_inserts_new_model(db_session_for_tests: Session):
    service = ClampsService(
        clamps_repository=PostgresClampsRepository(db_session_for_tests),
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    clamp_create = ClampCreate(
        name="Test Clamp",
        port_name="Test Port",
        port_pin=1,
        amperage_rating=100,
        phase="A",
        circuit_id=uuid4(),
        electric_sensor_id=uuid4(),
        clamp_id=uuid4()
    )
    clamps = service.create_clamp(clamp_create)
    clamps_model = db_session_for_tests.query(Clamp).all()
    assert len(clamps_model) == 1
    clamp_model = clamps_model[0]
    assert clamp_model.clamp_id == clamps.clamp_id
    assert clamp_model.name == clamps.name
    assert clamp_model.port_name == clamps.port_name
    assert clamp_model.port_pin == clamps.port_pin
    assert clamp_model.amperage_rating == clamps.amperage_rating
    assert clamp_model.phase == clamps.phase
    assert clamp_model.circuit_id == clamps.circuit_id
    assert clamp_model.electric_sensor_id == clamps.electric_sensor_id
    assert clamp_model.created_at == clamps.created_at
    assert clamp_model.updated_at == clamps.updated_at


def test_create_clamp_raises_error_if_clamp_exists(db_session_for_tests: Session):
    service = ClampsService(
        clamps_repository=PostgresClampsRepository(db_session_for_tests),
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    clamp_create = ClampCreate(
        name="Test Clamp",
        port_name="Test Port",
        port_pin=1,
        amperage_rating=100,
        phase="A",
        circuit_id=uuid4(),
        electric_sensor_id=uuid4(),
        clamp_id=uuid4()
    )
    service.create_clamp(clamp_create)
    with pytest.raises(ValueError):
        service.create_clamp(clamp_create)


def test_create_clamp_raises_error_if_wrong_enum(db_session_for_tests: Session):
    with pytest.raises(ValidationError):
        clamp_create = ClampCreate(
            name="Test Clamp",
            port_name="Test Port",
            port_pin=1,
            amperage_rating=100,
            phase="Wrong",
            circuit_id=uuid4(),
            electric_sensor_id=uuid4(),
            clamp_id=uuid4()
        )


def test_get_clamp_by_id_returns_correct_clamp(db_session_for_tests: Session):
    service = ClampsService(
        clamps_repository=PostgresClampsRepository(db_session_for_tests),
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    clamp_create = ClampCreate(
        name="Test Clamp",
        port_name="Test Port",
        port_pin=1,
        amperage_rating=100,
        phase="A",
        circuit_id=uuid4(),
        electric_sensor_id=uuid4(),
        clamp_id=uuid4()
    )
    clamp = service.create_clamp(clamp_create)
    clamp_model = service.get_clamp_by_id(clamp.clamp_id)
    assert clamp_model.clamp_id == clamp.clamp_id
    assert clamp_model.name == clamp.name
    assert clamp_model.port_name == clamp.port_name
    assert clamp_model.port_pin == clamp.port_pin
    assert clamp_model.amperage_rating == clamp.amperage_rating
    assert clamp_model.phase == clamp.phase
    assert clamp_model.circuit_id == clamp.circuit_id
    assert clamp_model.electric_sensor_id == clamp.electric_sensor_id
    assert clamp_model.created_at == clamp.created_at
    assert clamp_model.updated_at == clamp.updated_at


def test_get_clamp_by_id_returns_none_if_clampt_does_not_exist(db_session_for_tests: Session):
    service = ClampsService(
        clamps_repository=PostgresClampsRepository(db_session_for_tests),
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    clamp_model = service.get_clamp_by_id(uuid4())
    assert clamp_model is None


def test_get_clamp_by_attributes_returns_correct_clamp(db_session_for_tests: Session):
    service = ClampsService(
        clamps_repository=PostgresClampsRepository(db_session_for_tests),
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    circuit_id = uuid4()
    clamp_create = ClampCreate(
        name="Test Clamp",
        port_name="Test Port",
        port_pin=1,
        amperage_rating=100,
        phase="A",
        circuit_id=circuit_id,
        electric_sensor_id=uuid4(),
        clamp_id=uuid4()
    )
    clamp = service.create_clamp(clamp_create)
    clamp_model = service.get_clamp_by_attributes(
        name=clamp.name,
        phase=clamp.phase,
        circuit_id=circuit_id
    )
    assert clamp_model.clamp_id == clamp.clamp_id
    assert clamp_model.name == clamp.name
    assert clamp_model.port_name == clamp.port_name
    assert clamp_model.port_pin == clamp.port_pin
    assert clamp_model.amperage_rating == clamp.amperage_rating
    assert clamp_model.phase == clamp.phase
    assert clamp_model.circuit_id == clamp.circuit_id
    assert clamp_model.electric_sensor_id == clamp.electric_sensor_id
    assert clamp_model.created_at == clamp.created_at
    assert clamp_model.updated_at == clamp.updated_at


def test_get_clamp_by_attributes_returns_none_if_clamp_does_not_exist(db_session_for_tests: Session):
    service = ClampsService(
        clamps_repository=PostgresClampsRepository(db_session_for_tests),
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    circuit_model = service.get_clamp_by_attributes(
        name="Test Circuit",
        circuit_id=uuid4(),
        phase="A"
    )
    assert circuit_model is None


def test_get_clamps_by_circuit_returns_correct_clamps(db_session_for_tests: Session):
    service = ClampsService(
        clamps_repository=PostgresClampsRepository(db_session_for_tests),
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    circuit_id = uuid4()
    clamp_create = ClampCreate(
        name="Test Clamp",
        port_name="Test Port",
        port_pin=1,
        amperage_rating=100,
        phase="A",
        circuit_id=circuit_id,
        electric_sensor_id=uuid4(),
        clamp_id=uuid4()
    )
    clamp = service.create_clamp(clamp_create)
    clamps = service.get_clamps_by_circuit(circuit_id)
    assert len(clamps) == 1
    clamp_model = clamps[0]
    assert clamp_model.clamp_id == clamp.clamp_id
    assert clamp_model.name == clamp.name
    assert clamp_model.port_name == clamp.port_name
    assert clamp_model.port_pin == clamp.port_pin
    assert clamp_model.amperage_rating == clamp.amperage_rating
    assert clamp_model.phase == clamp.phase
    assert clamp_model.circuit_id == clamp.circuit_id
    assert clamp_model.electric_sensor_id == clamp.electric_sensor_id
    assert clamp_model.created_at == clamp.created_at
    assert clamp_model.updated_at == clamp.updated_at


def test_delete_clamp_deletes_correct_clamp(db_session_for_tests: Session):
    service = ClampsService(
        clamps_repository=PostgresClampsRepository(db_session_for_tests),
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    clamp_create = ClampCreate(
        name="Test Clamp",
        port_name="Test Port",
        port_pin=1,
        amperage_rating=100,
        phase="A",
        circuit_id=uuid4(),
        electric_sensor_id=uuid4(),
        clamp_id=uuid4()
    )
    clamp = service.create_clamp(clamp_create)
    service.delete_clamp(clamp.clamp_id)
    clamp_model = service.get_clamp_by_id(clamp.clamp_id)
    assert clamp_model is None
