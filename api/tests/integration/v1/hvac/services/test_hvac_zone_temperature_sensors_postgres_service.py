from uuid import uuid4, UUID
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.hvac.models.hvac_zone_temperature_sensor import HvacZoneTemperatureSensors
from app.v1.hvac.repositories.hvac_zone_temperature_sensors_repository import PostgresHvacZoneTemperatureSensorsRepository
from app.v1.hvac.schemas.hvac_zone_temperature_sensor import HvacZoneTemperatureSensorCreate
from app.v1.hvac.services.hvac_zone_temperature_sensors import HvacZoneTemperatureSensorsService


def test_create_hvac_zone_temperature_sensors_inserts_new_model(db_session_for_tests: Session):
    service = HvacZoneTemperatureSensorsService(
        hvac_zone_temperature_sensors_repository=PostgresHvacZoneTemperatureSensorsRepository(db_session_for_tests)
    )

    hvac_zone_temperature_sensors_create = HvacZoneTemperatureSensorCreate(
        hvac_zone_id=uuid4(),
        temperature_sensor_id=uuid4()
    )
    hvac_zone_temperature_sensors = service.create_hvac_zone_temperature_sensor(hvac_zone_temperature_sensors_create)

    hvac_zone_temperature_sensors_models = db_session_for_tests.query(HvacZoneTemperatureSensors).all()
    assert len(hvac_zone_temperature_sensors_models) == 1
    hvac_zone_temperature_sensors_model = hvac_zone_temperature_sensors_models[0]
    assert hvac_zone_temperature_sensors_model.hvac_zone_id == hvac_zone_temperature_sensors.hvac_zone_id
    assert hvac_zone_temperature_sensors_model.temperature_sensor_id == hvac_zone_temperature_sensors.temperature_sensor_id
    assert hvac_zone_temperature_sensors_model.hvac_zone_temperature_sensor_id == hvac_zone_temperature_sensors.hvac_zone_temperature_sensor_id
    assert hvac_zone_temperature_sensors_model.created_at == hvac_zone_temperature_sensors.created_at
    assert hvac_zone_temperature_sensors_model.updated_at == hvac_zone_temperature_sensors.updated_at


def test_create_hvac_zone_temperature_sensors_raises_error_if_hvac_zone_temperature_sensors_exists(db_session_for_tests: Session):
    service = HvacZoneTemperatureSensorsService(
        hvac_zone_temperature_sensors_repository=PostgresHvacZoneTemperatureSensorsRepository(db_session_for_tests)
    )

    hvac_zone_temperature_sensors_create = HvacZoneTemperatureSensorCreate(
        hvac_zone_id=uuid4(),
        temperature_sensor_id=uuid4()
    )
    service.create_hvac_zone_temperature_sensor(hvac_zone_temperature_sensors_create)
    with pytest.raises(IntegrityError):
        service.create_hvac_zone_temperature_sensor(hvac_zone_temperature_sensors_create)


def test_get_hvac_zone_temperature_sensors_returns_correct_model(db_session_for_tests: Session):
    service = HvacZoneTemperatureSensorsService(
        hvac_zone_temperature_sensors_repository=PostgresHvacZoneTemperatureSensorsRepository(db_session_for_tests)
    )

    hvac_zone_temperature_sensors_create = HvacZoneTemperatureSensorCreate(
        hvac_zone_id=uuid4(),
        temperature_sensor_id=uuid4()
    )
    hvac_zone_temperature_sensors = service.create_hvac_zone_temperature_sensor(hvac_zone_temperature_sensors_create)

    hvac_zone_temperature_sensors_model = service.get_hvac_zone_temperature_sensor_by_id(hvac_zone_temperature_sensors.hvac_zone_temperature_sensor_id)
    assert hvac_zone_temperature_sensors_model.hvac_zone_id == hvac_zone_temperature_sensors.hvac_zone_id
    assert hvac_zone_temperature_sensors_model.temperature_sensor_id == hvac_zone_temperature_sensors.temperature_sensor_id
    assert hvac_zone_temperature_sensors_model.hvac_zone_temperature_sensor_id == hvac_zone_temperature_sensors.hvac_zone_temperature_sensor_id
    assert hvac_zone_temperature_sensors_model.created_at == hvac_zone_temperature_sensors.created_at
    assert hvac_zone_temperature_sensors_model.updated_at == hvac_zone_temperature_sensors.updated_at


def test_get_hvac_zone_temperature_sensors_returns_none_if_hvac_zone_temperature_sensors_does_not_exist(db_session_for_tests: Session):
    service = HvacZoneTemperatureSensorsService(
        hvac_zone_temperature_sensors_repository=PostgresHvacZoneTemperatureSensorsRepository(db_session_for_tests)
    )

    hvac_zone_temperature_sensors_model = service.get_hvac_zone_temperature_sensor_by_id(uuid4())
    assert hvac_zone_temperature_sensors_model is None


def test_get_hvac_zone_temperature_sensor_by_attributes_returns_correct_model(db_session_for_tests: Session):
    service = HvacZoneTemperatureSensorsService(
        hvac_zone_temperature_sensors_repository=PostgresHvacZoneTemperatureSensorsRepository(db_session_for_tests)
    )

    hvac_zone_temperature_sensors_create = HvacZoneTemperatureSensorCreate(
        hvac_zone_id=uuid4(),
        temperature_sensor_id=uuid4()
    )
    hvac_zone_temperature_sensors = service.create_hvac_zone_temperature_sensor(hvac_zone_temperature_sensors_create)

    hvac_zone_temperature_sensors_model = service.get_hvac_zone_temperature_sensor_by_attributes(hvac_zone_temperature_sensors.hvac_zone_id, hvac_zone_temperature_sensors.temperature_sensor_id)
    assert hvac_zone_temperature_sensors_model.hvac_zone_id == hvac_zone_temperature_sensors.hvac_zone_id
    assert hvac_zone_temperature_sensors_model.temperature_sensor_id == hvac_zone_temperature_sensors.temperature_sensor_id
    assert hvac_zone_temperature_sensors_model.hvac_zone_temperature_sensor_id == hvac_zone_temperature_sensors.hvac_zone_temperature_sensor_id
    assert hvac_zone_temperature_sensors_model.created_at == hvac_zone_temperature_sensors.created_at
    assert hvac_zone_temperature_sensors_model.updated_at == hvac_zone_temperature_sensors.updated_at


def test_get_hvac_zone_temperature_sensor_by_attributes_returns_none_if_hvac_zone_temperature_sensors_does_not_exist(db_session_for_tests: Session):
    service = HvacZoneTemperatureSensorsService(
        hvac_zone_temperature_sensors_repository=PostgresHvacZoneTemperatureSensorsRepository(db_session_for_tests)
    )

    hvac_zone_temperature_sensors_model = service.get_hvac_zone_temperature_sensor_by_attributes(uuid4(), uuid4())
    assert hvac_zone_temperature_sensors_model is None


def test_get_hvac_zone_temperature_sensors_by_hvac_zone_id_returns_correct_models(db_session_for_tests: Session):
    service = HvacZoneTemperatureSensorsService(
        hvac_zone_temperature_sensors_repository=PostgresHvacZoneTemperatureSensorsRepository(db_session_for_tests)
    )

    hvac_zone_id = uuid4()
    temperature_sensor_ids = [uuid4(), uuid4()]
    for temperature_sensor_id in temperature_sensor_ids:
        hvac_zone_temperature_sensors_create = HvacZoneTemperatureSensorCreate(
            hvac_zone_id=hvac_zone_id,
            temperature_sensor_id=temperature_sensor_id
        )
        service.create_hvac_zone_temperature_sensor(hvac_zone_temperature_sensors_create)

    hvac_zone_temperature_sensors_models = service.get_hvac_zone_temperature_sensors_by_hvac_zone_id(hvac_zone_id)
    assert len(hvac_zone_temperature_sensors_models) == 2
    for hvac_zone_temperature_sensors_model in hvac_zone_temperature_sensors_models:
        assert hvac_zone_temperature_sensors_model.hvac_zone_id == hvac_zone_id
        assert hvac_zone_temperature_sensors_model.temperature_sensor_id in temperature_sensor_ids


def test_delete_hvac_zone_temperature_sensor_deletes_model(db_session_for_tests: Session):
    service = HvacZoneTemperatureSensorsService(
        hvac_zone_temperature_sensors_repository=PostgresHvacZoneTemperatureSensorsRepository(db_session_for_tests)
    )

    hvac_zone_temperature_sensors_create = HvacZoneTemperatureSensorCreate(
        hvac_zone_id=uuid4(),
        temperature_sensor_id=uuid4()
    )
    hvac_zone_temperature_sensors = service.create_hvac_zone_temperature_sensor(hvac_zone_temperature_sensors_create)

    service.delete_hvac_zone_temperature_sensor(hvac_zone_temperature_sensors.hvac_zone_temperature_sensor_id)

    hvac_zone_temperature_sensors_model = service.get_hvac_zone_temperature_sensor_by_id(hvac_zone_temperature_sensors.hvac_zone_temperature_sensor_id)
    assert hvac_zone_temperature_sensors_model is None
