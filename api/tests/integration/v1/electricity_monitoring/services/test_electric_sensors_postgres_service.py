from uuid import uuid4
import pytest
from sqlalchemy.orm import Session

from app.v1.electricity_monitoring.models.electric_sensor import ElectricSensor
from app.v1.electricity_monitoring.repositories.electric_sensors_repository import PostgresElectricSensorsRepository
from app.v1.electricity_monitoring.schemas.electric_sensor import ElectricSensorCreate
from app.v1.electricity_monitoring.services.electric_sensors import ElectricSensorsService


def test_create_electric_sensor_inserts_new_model(db_session_for_tests: Session):
    service = ElectricSensorsService(
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    electric_sensor_create = ElectricSensorCreate(
        name="Test Electric Sensor",
        duid="aaaaaaaa",
        port_count=1,
        electric_panel_id=uuid4(),
        gateway_id=uuid4(),
        a_breaker_num=1,
        b_breaker_num=2,
        c_breaker_num=3,
        electric_sensor_id=uuid4()
    )
    electric_sensors = service.create_electric_sensor(electric_sensor_create)
    electric_sensors_model = db_session_for_tests.query(ElectricSensor).all()
    assert len(electric_sensors_model) == 1
    electric_sensor_model = electric_sensors_model[0]
    assert electric_sensor_model.electric_sensor_id == electric_sensors.electric_sensor_id
    assert electric_sensor_model.name == electric_sensors.name
    assert electric_sensor_model.port_count == electric_sensors.port_count
    assert electric_sensor_model.electric_panel_id == electric_sensors.electric_panel_id
    assert electric_sensor_model.gateway_id == electric_sensors.gateway_id
    assert electric_sensor_model.a_breaker_num == electric_sensors.a_breaker_num
    assert electric_sensor_model.b_breaker_num == electric_sensors.b_breaker_num
    assert electric_sensor_model.c_breaker_num == electric_sensors.c_breaker_num
    assert electric_sensor_model.created_at == electric_sensors.created_at
    assert electric_sensor_model.updated_at == electric_sensors.updated_at


def test_create_electric_sensor_raises_error_if_electric_sensor_exists(db_session_for_tests: Session):
    service = ElectricSensorsService(
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    electric_sensor_create = ElectricSensorCreate(
        name="Test Electric Sensor",
        duid="aaaaaaaa",
        port_count=1,
        electric_panel_id=uuid4(),
        gateway_id=uuid4(),
        a_breaker_num=1,
        b_breaker_num=2,
        c_breaker_num=3,
        electric_sensor_id=uuid4()
    )
    service.create_electric_sensor(electric_sensor_create)
    with pytest.raises(ValueError):
        service.create_electric_sensor(electric_sensor_create)


def test_get_electric_sensor_by_id_returns_correct_sensor(db_session_for_tests: Session):
    service = ElectricSensorsService(
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    electric_sensor_create = ElectricSensorCreate(
        name="Test Electric Sensor",
        duid="aaaaaaaa",
        port_count=1,
        electric_panel_id=uuid4(),
        gateway_id=uuid4(),
        a_breaker_num=1,
        b_breaker_num=2,
        c_breaker_num=3,
        electric_sensor_id=uuid4()
    )
    electric_sensor = service.create_electric_sensor(electric_sensor_create)
    electric_sensor_model = service.get_electric_sensor_by_id(electric_sensor.electric_sensor_id)
    assert electric_sensor_model.electric_sensor_id == electric_sensor.electric_sensor_id
    assert electric_sensor_model.name == electric_sensor.name
    assert electric_sensor_model.port_count == electric_sensor.port_count
    assert electric_sensor_model.electric_panel_id == electric_sensor.electric_panel_id
    assert electric_sensor_model.gateway_id == electric_sensor.gateway_id
    assert electric_sensor_model.a_breaker_num == electric_sensor.a_breaker_num
    assert electric_sensor_model.b_breaker_num == electric_sensor.b_breaker_num
    assert electric_sensor_model.c_breaker_num == electric_sensor.c_breaker_num
    assert electric_sensor_model.created_at == electric_sensor.created_at
    assert electric_sensor_model.updated_at == electric_sensor.updated_at


def test_get_electric_sensor_by_id_returns_none_if_electric_sensor_does_not_exist(db_session_for_tests: Session):
    service = ElectricSensorsService(
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    electric_sensor_model = service.get_electric_sensor_by_id(uuid4())
    assert electric_sensor_model is None


def test_get_electric_sensor_by_attributes_returns_correct_sensor(db_session_for_tests: Session):
    service = ElectricSensorsService(
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    gateway_id = uuid4()
    electric_panel_id = uuid4()
    electric_sensor_create = ElectricSensorCreate(
        name="Test Electric Sensor",
        duid="aaaaaaaa",
        port_count=1,
        electric_panel_id=electric_panel_id,
        gateway_id=gateway_id,
        a_breaker_num=1,
        b_breaker_num=2,
        c_breaker_num=3,
        electric_sensor_id=uuid4()
    )
    electric_sensor = service.create_electric_sensor(electric_sensor_create)
    electric_sensor_model = service.get_electric_sensor_by_attributes(
        name=electric_sensor.name,
        gateway_id=gateway_id,
        electric_panel_id=electric_panel_id
    )
    assert electric_sensor_model.electric_sensor_id == electric_sensor.electric_sensor_id
    assert electric_sensor_model.name == electric_sensor.name
    assert electric_sensor_model.port_count == electric_sensor.port_count
    assert electric_sensor_model.electric_panel_id == electric_sensor.electric_panel_id
    assert electric_sensor_model.gateway_id == electric_sensor.gateway_id
    assert electric_sensor_model.a_breaker_num == electric_sensor.a_breaker_num
    assert electric_sensor_model.b_breaker_num == electric_sensor.b_breaker_num
    assert electric_sensor_model.c_breaker_num == electric_sensor.c_breaker_num
    assert electric_sensor_model.created_at == electric_sensor.created_at
    assert electric_sensor_model.updated_at == electric_sensor.updated_at


def test_get_electric_sensor_by_attributes_returns_none_if_sensor_does_not_exist(db_session_for_tests: Session):
    service = ElectricSensorsService(
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    electric_sensor_model = service.get_electric_sensor_by_attributes(
        name="Test Electric Sensor",
        gateway_id=uuid4(),
        electric_panel_id=uuid4()
    )
    assert electric_sensor_model is None


def test_get_electric_sensors_by_gateway_returns_correct_sensors(db_session_for_tests: Session):
    service = ElectricSensorsService(
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    gateway_id = uuid4()
    electric_sensor_create = ElectricSensorCreate(
        name="Test Electric Sensor",
        duid="aaaaaaaa",
        port_count=1,
        electric_panel_id=uuid4(),
        gateway_id=gateway_id,
        a_breaker_num=1,
        b_breaker_num=2,
        c_breaker_num=3,
        electric_sensor_id=uuid4()
    )
    electric_sensor = service.create_electric_sensor(electric_sensor_create)
    electric_sensors = service.get_electric_sensors_by_gateway(gateway_id)
    assert len(electric_sensors) == 1
    electric_sensor_model = electric_sensors[0]
    assert electric_sensor_model.electric_sensor_id == electric_sensor.electric_sensor_id
    assert electric_sensor_model.name == electric_sensor.name
    assert electric_sensor_model.port_count == electric_sensor.port_count
    assert electric_sensor_model.electric_panel_id == electric_sensor.electric_panel_id
    assert electric_sensor_model.gateway_id == electric_sensor.gateway_id
    assert electric_sensor_model.a_breaker_num == electric_sensor.a_breaker_num
    assert electric_sensor_model.b_breaker_num == electric_sensor.b_breaker_num
    assert electric_sensor_model.c_breaker_num == electric_sensor.c_breaker_num
    assert electric_sensor_model.created_at == electric_sensor.created_at
    assert electric_sensor_model.updated_at == electric_sensor.updated_at


def test_delete_electric_sensor_deletes_correct_sensor(db_session_for_tests: Session):
    service = ElectricSensorsService(
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session_for_tests)
    )
    electric_sensor_create = ElectricSensorCreate(
        name="Test Electric Sensor",
        duid="aaaaaaaa",
        port_count=1,
        electric_panel_id=uuid4(),
        gateway_id=uuid4(),
        a_breaker_num=1,
        b_breaker_num=2,
        c_breaker_num=3,
        electric_sensor_id=uuid4()
    )
    electric_sensor = service.create_electric_sensor(electric_sensor_create)
    service.delete_electric_sensor(electric_sensor.electric_sensor_id)
    electric_sensor_model = service.get_electric_sensor_by_id(electric_sensor.electric_sensor_id)
    assert electric_sensor_model is None
