from uuid import uuid4, UUID
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.hvac.models.thermostat import Thermostat
from app.v1.hvac.repositories.thermostats_repository import PostgresThermostatsRepository
from app.v1.hvac.schemas.thermostat import ThermostatCreate, ThermostatModelEnum
from app.v1.hvac.services.thermostats import ThermostatsService


def test_create_thermostats_inserts_new_model(db_session_for_tests: Session):
    service = ThermostatsService(
        thermostats_repository=PostgresThermostatsRepository(db_session_for_tests)
    )

    thermostats_create = ThermostatCreate(
        name='Test Thermostat',
        duid='1234567890',
        modbus_address=0,
        model=ThermostatModelEnum.v1,
        node_id=uuid4(),
        hvac_zone_id=uuid4()
    )
    thermostats = service.create_thermostat(thermostats_create)

    thermostats_models = db_session_for_tests.query(Thermostat).all()
    assert len(thermostats_models) == 1
    thermostats_model = thermostats_models[0]
    assert thermostats_model.name == thermostats.name
    assert thermostats_model.duid == thermostats.duid
    assert thermostats_model.modbus_address == thermostats.modbus_address
    assert thermostats_model.model == thermostats.model
    assert thermostats_model.node_id == thermostats.node_id
    assert thermostats_model.hvac_zone_id == thermostats.hvac_zone_id
    assert thermostats_model.created_at == thermostats.created_at
    assert thermostats_model.updated_at == thermostats.updated_at


def test_create_thermostats_raises_error_if_thermostats_exists(db_session_for_tests: Session):
    service = ThermostatsService(
        thermostats_repository=PostgresThermostatsRepository(db_session_for_tests)
    )

    thermostats_create = ThermostatCreate(
        name='Test Thermostat',
        duid='1234567890',
        modbus_address=0,
        model=ThermostatModelEnum.v1,
        node_id=uuid4(),
        hvac_zone_id=uuid4()
    )
    service.create_thermostat(thermostats_create)
    with pytest.raises(ValueError):
        service.create_thermostat(thermostats_create)


def test_get_thermostats_returns_correct_model(db_session_for_tests: Session):
    service = ThermostatsService(
        thermostats_repository=PostgresThermostatsRepository(db_session_for_tests)
    )

    thermostats_create = ThermostatCreate(
        name='Test Thermostat',
        duid='1234567890',
        modbus_address=0,
        model=ThermostatModelEnum.v1,
        node_id=uuid4(),
        hvac_zone_id=uuid4()
    )
    thermostats = service.create_thermostat(thermostats_create)

    thermostats_model = service.get_thermostat_by_id(thermostats.thermostat_id)
    assert thermostats_model.name == thermostats.name
    assert thermostats_model.duid == thermostats.duid
    assert thermostats_model.modbus_address == thermostats.modbus_address
    assert thermostats_model.model == thermostats.model
    assert thermostats_model.node_id == thermostats.node_id
    assert thermostats_model.hvac_zone_id == thermostats.hvac_zone_id
    assert thermostats_model.created_at == thermostats.created_at
    assert thermostats_model.updated_at == thermostats.updated_at


def test_get_thermostats_returns_none_if_thermostats_does_not_exist(db_session_for_tests: Session):
    service = ThermostatsService(
        thermostats_repository=PostgresThermostatsRepository(db_session_for_tests)
    )

    thermostats_model = service.get_thermostat_by_id(uuid4())
    assert thermostats_model is None


def test_get_thermostats_returns_correct_model_by_attributes(db_session_for_tests: Session):
    service = ThermostatsService(
        thermostats_repository=PostgresThermostatsRepository(db_session_for_tests)
    )

    thermostats_create = ThermostatCreate(
        name='Test Thermostat',
        duid='1234567890',
        modbus_address=0,
        model=ThermostatModelEnum.v1,
        node_id=uuid4(),
        hvac_zone_id=uuid4()
    )
    thermostats = service.create_thermostat(thermostats_create)
    thermostats_model = service.get_thermostat_by_attributes(thermostats.name, thermostats.duid, thermostats.model, thermostats.node_id, thermostats.hvac_zone_id)

    assert thermostats_model.name == thermostats.name
    assert thermostats_model.duid == thermostats.duid
    assert thermostats_model.modbus_address == thermostats.modbus_address
    assert thermostats_model.model == thermostats.model
    assert thermostats_model.node_id == thermostats.node_id
    assert thermostats_model.hvac_zone_id == thermostats.hvac_zone_id
    assert thermostats_model.created_at == thermostats.created_at
    assert thermostats_model.updated_at == thermostats.updated_at


def test_delete_thermostat_deletes_thermostat(db_session_for_tests: Session):
    service = ThermostatsService(
        thermostats_repository=PostgresThermostatsRepository(db_session_for_tests)
    )

    thermostats_create = ThermostatCreate(
        name='Test Thermostat',
        duid='1234567890',
        modbus_address=0,
        model=ThermostatModelEnum.v1,
        node_id=uuid4(),
        hvac_zone_id=uuid4()
    )
    thermostats = service.create_thermostat(thermostats_create)

    service.delete_thermostat(thermostats.thermostat_id)
    thermostat_model = service.get_thermostat_by_id(thermostats.thermostat_id)
    assert thermostat_model is None
