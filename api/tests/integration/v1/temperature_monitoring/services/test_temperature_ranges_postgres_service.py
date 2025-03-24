from uuid import uuid4, UUID

import pytest

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.temperature_monitoring.models.temperature_range import TemperatureRange
from app.v1.temperature_monitoring.repositories.temperature_ranges_repository import PostgresTemperatureRangesRepository
from app.v1.temperature_monitoring.schemas.temperature_range import TemperatureRangeCreate, TemperatureRangeWarningLevelEnum
from app.v1.temperature_monitoring.services.temperature_ranges import TemperatureRangesService


def test_create_temperature_range_inserts_new_model(db_session_for_tests: Session):
    service = TemperatureRangesService(
        temperature_ranges_repository=PostgresTemperatureRangesRepository(db_session_for_tests)
    )
    temperature_range_create = TemperatureRangeCreate(
        high_degrees_celcius=30.0,
        low_degrees_celcius=20.0,
        warning_level=TemperatureRangeWarningLevelEnum.WARNING,
        temperature_sensor_place_id=uuid4()
    )
    temperature_range = service.create_temperature_range(temperature_range_create)
    temperature_range_models = db_session_for_tests.query(TemperatureRange).all()
    assert len(temperature_range_models) == 1
    temperature_range_model = temperature_range_models[0]
    assert temperature_range_model.temperature_range_id == temperature_range.temperature_range_id
    assert temperature_range_model.high_degrees_celcius == temperature_range.high_degrees_celcius
    assert temperature_range_model.low_degrees_celcius == temperature_range.low_degrees_celcius
    assert temperature_range_model.warning_level == temperature_range.warning_level
    assert temperature_range_model.temperature_sensor_place_id == temperature_range.temperature_sensor_place_id
    assert temperature_range_model.created_at == temperature_range.created_at
    assert temperature_range_model.updated_at == temperature_range.updated_at


def test_create_temperature_range_raises_error_if_temperature_range_exists(db_session_for_tests: Session):
    service = TemperatureRangesService(
        temperature_ranges_repository=PostgresTemperatureRangesRepository(db_session_for_tests)
    )
    temperature_range_create = TemperatureRangeCreate(
        high_degrees_celcius=30.0,
        low_degrees_celcius=20.0,
        warning_level=TemperatureRangeWarningLevelEnum.WARNING,
        temperature_sensor_place_id=uuid4()
    )
    service.create_temperature_range(temperature_range_create)
    with pytest.raises(IntegrityError):
        service.create_temperature_range(temperature_range_create)


def test_get_temperature_ranges_by_temperature_sensor_id_returns_correct_models(db_session_for_tests: Session):
    service = TemperatureRangesService(
        temperature_ranges_repository=PostgresTemperatureRangesRepository(db_session_for_tests)
    )
    temperature_sensor_id = uuid4()
    temperature_range_create = TemperatureRangeCreate(
        high_degrees_celcius=30.0,
        low_degrees_celcius=20.0,
        warning_level=TemperatureRangeWarningLevelEnum.WARNING,
        temperature_sensor_place_id=temperature_sensor_id
    )
    service.create_temperature_range(
        TemperatureRangeCreate(
            high_degrees_celcius=40.0,
            low_degrees_celcius=30.0,
            warning_level=TemperatureRangeWarningLevelEnum.GOOD,
            temperature_sensor_place_id=uuid4()
        )
    )
    temperature_range = service.create_temperature_range(temperature_range_create)
    temperature_ranges = service.get_temperature_ranges_by_temperature_sensor_place_id(temperature_sensor_id)
    assert len(temperature_ranges) == 1
    assert temperature_ranges[0] == temperature_range


def test_get_temperature_ranges_by_temperature_sensor_id_returns_empty_list_if_no_models(db_session_for_tests: Session):
    service = TemperatureRangesService(
        temperature_ranges_repository=PostgresTemperatureRangesRepository(db_session_for_tests)
    )
    service.create_temperature_range(
        TemperatureRangeCreate(
            high_degrees_celcius=40.0,
            low_degrees_celcius=30.0,
            warning_level=TemperatureRangeWarningLevelEnum.GOOD,
            temperature_sensor_place_id=uuid4()
        )
    )
    temperature_ranges = service.get_temperature_ranges_by_temperature_sensor_place_id(uuid4())
    assert len(temperature_ranges) == 0


def test_get_temperature_range_by_id_returns_correct_model(db_session_for_tests: Session):
    service = TemperatureRangesService(
        temperature_ranges_repository=PostgresTemperatureRangesRepository(db_session_for_tests)
    )
    temperature_range_create = TemperatureRangeCreate(
        high_degrees_celcius=30.0,
        low_degrees_celcius=20.0,
        warning_level=TemperatureRangeWarningLevelEnum.WARNING,
        temperature_sensor_place_id=uuid4()
    )
    service.create_temperature_range(
        TemperatureRangeCreate(
            high_degrees_celcius=40.0,
            low_degrees_celcius=30.0,
            warning_level=TemperatureRangeWarningLevelEnum.GOOD,
            temperature_sensor_place_id=uuid4()
        )
    )
    temperature_range = service.create_temperature_range(temperature_range_create)
    temperature_range_model = service.get_temperature_range_by_id(temperature_range.temperature_range_id)
    assert temperature_range_model == temperature_range


def test_get_temperature_range_by_id_returns_none_if_no_model(db_session_for_tests: Session):
    service = TemperatureRangesService(
        temperature_ranges_repository=PostgresTemperatureRangesRepository(db_session_for_tests)
    )
    service.create_temperature_range(
        TemperatureRangeCreate(
            high_degrees_celcius=40.0,
            low_degrees_celcius=30.0,
            warning_level=TemperatureRangeWarningLevelEnum.GOOD,
            temperature_sensor_place_id=uuid4()
        )
    )
    temperature_range_model = service.get_temperature_range_by_id(uuid4())
    assert temperature_range_model is None


def test_get_temperature_range_for_temperature_sensor_by_id_returns_correct_model(db_session_for_tests: Session):
    service = TemperatureRangesService(
        temperature_ranges_repository=PostgresTemperatureRangesRepository(db_session_for_tests)
    )
    temperature_sensor_id = uuid4()
    temperature_range_create = TemperatureRangeCreate(
        high_degrees_celcius=30.0,
        low_degrees_celcius=20.0,
        warning_level=TemperatureRangeWarningLevelEnum.WARNING,
        temperature_sensor_place_id=temperature_sensor_id
    )
    service.create_temperature_range(
        TemperatureRangeCreate(
            high_degrees_celcius=40.0,
            low_degrees_celcius=30.0,
            warning_level=TemperatureRangeWarningLevelEnum.GOOD,
            temperature_sensor_place_id=uuid4()
        )
    )
    temperature_range = service.create_temperature_range(temperature_range_create)
    temperature_range_model = service.get_temperature_range_for_temperature_sensor_place_by_id(temperature_sensor_id, temperature_range.temperature_range_id)
    assert temperature_range_model == temperature_range


def test_get_temperature_range_for_temperature_sensor_by_id_returns_none_if_no_model(db_session_for_tests: Session):
    service = TemperatureRangesService(
        temperature_ranges_repository=PostgresTemperatureRangesRepository(db_session_for_tests)
    )
    temperature_sensor_id = uuid4()
    service.create_temperature_range(
        TemperatureRangeCreate(
            high_degrees_celcius=40.0,
            low_degrees_celcius=30.0,
            warning_level=TemperatureRangeWarningLevelEnum.GOOD,
            temperature_sensor_place_id=uuid4()
        )
    )
    temperature_range_model = service.get_temperature_range_for_temperature_sensor_place_by_id(temperature_sensor_id, uuid4())
    assert temperature_range_model is None


def test_delete_temperature_range_by_id_deletes_correct_model(db_session_for_tests: Session):
    service = TemperatureRangesService(
        temperature_ranges_repository=PostgresTemperatureRangesRepository(db_session_for_tests)
    )
    temperature_range_create = TemperatureRangeCreate(
        high_degrees_celcius=30.0,
        low_degrees_celcius=20.0,
        warning_level=TemperatureRangeWarningLevelEnum.WARNING,
        temperature_sensor_place_id=uuid4()
    )
    service.create_temperature_range(
        TemperatureRangeCreate(
            high_degrees_celcius=40.0,
            low_degrees_celcius=30.0,
            warning_level=TemperatureRangeWarningLevelEnum.GOOD,
            temperature_sensor_place_id=uuid4()
        )
    )
    temperature_range = service.create_temperature_range(temperature_range_create)
    service.delete_temperature_range_by_id(temperature_range.temperature_range_id)
    temperature_ranges = db_session_for_tests.query(TemperatureRange).all()
    assert len(temperature_ranges) == 1
    assert temperature_ranges[0] != temperature_range
