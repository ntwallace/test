from uuid import uuid4

import pytest

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.temperature_monitoring.models.temperature_sensor import TemperatureSensor
from app.v1.temperature_monitoring.repositories.temperature_sensors_repository import PostgresTemperatureSensorsRepository
from app.v1.temperature_monitoring.schemas.temperature_sensor import (
    TemperatureSensorCreate,
    TemperatureSensorMakeEnum,
    TemperatureSensorModelEnum,
)
from app.v1.temperature_monitoring.services.temperature_sensors import TemperatureSensorsService


def test_create_temperature_sensor_inserts_new_model(db_session_for_tests: Session):
    service = TemperatureSensorsService(
        temperature_sensors_repository=PostgresTemperatureSensorsRepository(db_session_for_tests)
    )
    temperature_sensor_create = TemperatureSensorCreate(
        name="Test Temperature Sensor",
        duid="test_duid",
        make=TemperatureSensorMakeEnum.MINEW,
        model=TemperatureSensorModelEnum.MST01_01,
        gateway_id=uuid4(),
        location_id=uuid4()
    )
    temperature_sensor = service.create_temperature_sensor(temperature_sensor_create)
    temperature_sensor_models = db_session_for_tests.query(TemperatureSensor).all()
    assert len(temperature_sensor_models) == 1
    temperature_sensor_model = temperature_sensor_models[0]
    assert temperature_sensor_model.temperature_sensor_id == temperature_sensor.temperature_sensor_id
    assert temperature_sensor_model.name == temperature_sensor.name
    assert temperature_sensor_model.duid == temperature_sensor.duid
    assert temperature_sensor_model.make == temperature_sensor.make
    assert temperature_sensor_model.model == temperature_sensor.model
    assert temperature_sensor_model.gateway_id == temperature_sensor.gateway_id
    assert temperature_sensor_model.location_id == temperature_sensor.location_id
    assert temperature_sensor_model.created_at == temperature_sensor.created_at
    assert temperature_sensor_model.updated_at == temperature_sensor.updated_at


def test_create_temperature_sensor_raises_error_if_temperature_sensor_exists(db_session_for_tests: Session):
    service = TemperatureSensorsService(
        temperature_sensors_repository=PostgresTemperatureSensorsRepository(db_session_for_tests)
    )
    temperature_sensor_create = TemperatureSensorCreate(
        name="Test Temperature Sensor",
        duid="test_duid",
        make=TemperatureSensorMakeEnum.MINEW,
        model=TemperatureSensorModelEnum.MST01_01,
        gateway_id=uuid4(),
        location_id=uuid4()
    )
    service.create_temperature_sensor(temperature_sensor_create)
    with pytest.raises(IntegrityError):
        service.create_temperature_sensor(temperature_sensor_create)


def test_filter_by_returns_correct_temperature_sensors(db_session_for_tests: Session):
    service = TemperatureSensorsService(
        temperature_sensors_repository=PostgresTemperatureSensorsRepository(db_session_for_tests)
    )
    temperature_sensor_create = TemperatureSensorCreate(
        name="Test Temperature Sensor",
        duid="test_duid",
        make=TemperatureSensorMakeEnum.MINEW,
        model=TemperatureSensorModelEnum.MST01_01,
        gateway_id=uuid4(),
        location_id=uuid4()
    )
    service.create_temperature_sensor(
        TemperatureSensorCreate(
            name="Test Temperature Sensor2",
            duid="test_duid2",
            make=TemperatureSensorMakeEnum.MINEW,
            model=TemperatureSensorModelEnum.MST01_01,
            gateway_id=uuid4(),
            location_id=uuid4()
        )
    )
    
    temperature_sensor = service.create_temperature_sensor(temperature_sensor_create)
    temperature_sensor_models = service.filter_by(location_id=temperature_sensor.location_id)
    assert len(temperature_sensor_models) == 1
    assert temperature_sensor_models[0] == temperature_sensor


def test_filter_by_returns_empty_list_if_no_temperature_sensors_found(db_session_for_tests: Session):
    service = TemperatureSensorsService(
        temperature_sensors_repository=PostgresTemperatureSensorsRepository(db_session_for_tests)
    )
    temperature_sensor_create = TemperatureSensorCreate(
        name="Test Temperature Sensor",
        duid="test_duid",
        make=TemperatureSensorMakeEnum.MINEW,
        model=TemperatureSensorModelEnum.MST01_01,
        gateway_id=uuid4(),
        location_id=uuid4()
    )
    service.create_temperature_sensor(temperature_sensor_create)
    temperature_sensor_models = service.filter_by(location_id=uuid4())
    assert len(temperature_sensor_models) == 0


def test_get_temperature_sensor_by_id_returns_correct_temperature_sensor(db_session_for_tests: Session):
    service = TemperatureSensorsService(
        temperature_sensors_repository=PostgresTemperatureSensorsRepository(db_session_for_tests)
    )
    temperature_sensor_create = TemperatureSensorCreate(
        name="Test Temperature Sensor",
        duid="test_duid",
        make=TemperatureSensorMakeEnum.MINEW,
        model=TemperatureSensorModelEnum.MST01_01,
        gateway_id=uuid4(),
        location_id=uuid4()
    )
    service.create_temperature_sensor(
        TemperatureSensorCreate(
            name="Test Temperature Sensor2",
            duid="test_duid2",
            make=TemperatureSensorMakeEnum.MINEW,
            model=TemperatureSensorModelEnum.MST01_01,
            gateway_id=uuid4(),
            location_id=uuid4()
        )
    )
    temperature_sensor = service.create_temperature_sensor(temperature_sensor_create)
    temperature_sensor_model = service.get_temperature_sensor_by_id(temperature_sensor.temperature_sensor_id)
    assert temperature_sensor_model == temperature_sensor


def test_get_temperature_sensor_by_id_returns_none_if_temperature_sensor_not_found(db_session_for_tests: Session):
    service = TemperatureSensorsService(
        temperature_sensors_repository=PostgresTemperatureSensorsRepository(db_session_for_tests)
    )
    temperature_sensor_create = TemperatureSensorCreate(
        name="Test Temperature Sensor",
        duid="test_duid",
        make=TemperatureSensorMakeEnum.MINEW,
        model=TemperatureSensorModelEnum.MST01_01,
        gateway_id=uuid4(),
        location_id=uuid4()
    )
    service.create_temperature_sensor(temperature_sensor_create)
    temperature_sensor_model = service.get_temperature_sensor_by_id(uuid4())
    assert temperature_sensor_model is None


def test_delete_temperature_sensor_removes_temperature_sensor_from_db(db_session_for_tests: Session):
    service = TemperatureSensorsService(
        temperature_sensors_repository=PostgresTemperatureSensorsRepository(db_session_for_tests)
    )
    temperature_sensor_create = TemperatureSensorCreate(
        name="Test Temperature Sensor",
        duid="test_duid",
        make=TemperatureSensorMakeEnum.MINEW,
        model=TemperatureSensorModelEnum.MST01_01,
        gateway_id=uuid4(),
        location_id=uuid4()
    )
    temperature_sensor = service.create_temperature_sensor(temperature_sensor_create)
    service.delete_temperature_sensor(temperature_sensor.temperature_sensor_id)
    temperature_sensor_models = db_session_for_tests.query(TemperatureSensor).all()
    assert len(temperature_sensor_models) == 0
