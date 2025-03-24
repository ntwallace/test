from uuid import uuid4, UUID

import pytest

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.temperature_monitoring.models.temperature_sensor_place import TemperatureSensorPlace
from app.v1.temperature_monitoring.repositories.temperature_sensor_places_repository import PostgresTemperatureSensorPlacesRepository
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import (
    TemperatureSensorPlaceCreate,
    TemperatureSensorPlaceType,
)
from app.v1.temperature_monitoring.services.temperature_sensor_places import TemperatureSensorPlacesService


def test_create_temperature_sensor_place_inserts_new_model(db_session_for_tests: Session):
    service = TemperatureSensorPlacesService(
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session_for_tests)
    )
    temperature_sensor_place_create = TemperatureSensorPlaceCreate(
        name="Test Temperature Sensor Place",
        temperature_sensor_place_type=TemperatureSensorPlaceType.APPLIANCE,
        location_id=uuid4(),
        temperature_sensor_id=uuid4()
    )
    temperature_sensor_place = service.create_temperature_sensor_place(temperature_sensor_place_create)
    temperature_sensor_place_models = db_session_for_tests.query(TemperatureSensorPlace).all()
    assert len(temperature_sensor_place_models) == 1
    temperature_sensor_place_model = temperature_sensor_place_models[0]
    assert temperature_sensor_place_model.temperature_sensor_place_id == temperature_sensor_place.temperature_sensor_place_id
    assert temperature_sensor_place_model.name == temperature_sensor_place.name
    assert temperature_sensor_place_model.temperature_sensor_place_type == temperature_sensor_place.temperature_sensor_place_type
    assert temperature_sensor_place_model.location_id == temperature_sensor_place.location_id
    assert temperature_sensor_place_model.temperature_sensor_id == temperature_sensor_place.temperature_sensor_id
    assert temperature_sensor_place_model.created_at == temperature_sensor_place.created_at
    assert temperature_sensor_place_model.updated_at == temperature_sensor_place.updated_at


def test_create_temperature_sensor_place_raises_error_if_temperature_sensor_place_exists(db_session_for_tests: Session):
    service = TemperatureSensorPlacesService(
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session_for_tests)
    )
    temperature_sensor_place_create = TemperatureSensorPlaceCreate(
        name="Test Temperature Sensor Place",
        temperature_sensor_place_type=TemperatureSensorPlaceType.APPLIANCE,
        location_id=uuid4(),
        temperature_sensor_id=uuid4()
    )
    service.create_temperature_sensor_place(temperature_sensor_place_create)
    with pytest.raises(IntegrityError):
        service.create_temperature_sensor_place(temperature_sensor_place_create)


def test_get_temperature_sensor_places_for_location_returns_correct_temperature_sensor_places(db_session_for_tests: Session):
    service = TemperatureSensorPlacesService(
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session_for_tests)
    )
    temperature_sensor_place_create = TemperatureSensorPlaceCreate(
        name="Test Temperature Sensor Place",
        temperature_sensor_place_type=TemperatureSensorPlaceType.APPLIANCE,
        location_id=uuid4(),
        temperature_sensor_id=uuid4()
    )
    service.create_temperature_sensor_place(
        TemperatureSensorPlaceCreate(
            name="Test Temperature Sensor Place 2",
            temperature_sensor_place_type=TemperatureSensorPlaceType.APPLIANCE,
            location_id=uuid4(),
            temperature_sensor_id=uuid4()
        )
    )
    
    temperature_sensor_place = service.create_temperature_sensor_place(temperature_sensor_place_create)
    temperature_sensor_place_models = service.get_temperature_sensor_places_for_location(temperature_sensor_place.location_id)
    assert len(temperature_sensor_place_models) == 1
    assert temperature_sensor_place_models[0] == temperature_sensor_place


def test_get_temperature_sensor_places_for_location_returns_empty_list_if_no_temperature_sensor_places_found(db_session_for_tests: Session):
    service = TemperatureSensorPlacesService(
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session_for_tests)
    )
    temperature_sensor_place_create = TemperatureSensorPlaceCreate(
        name="Test Temperature Sensor Place",
        temperature_sensor_place_type=TemperatureSensorPlaceType.APPLIANCE,
        location_id=uuid4(),
        temperature_sensor_id=uuid4()
    )
    service.create_temperature_sensor_place(temperature_sensor_place_create)
    temperature_sensor_place_models = service.get_temperature_sensor_places_for_location(uuid4())
    assert len(temperature_sensor_place_models) == 0


def test_get_temperature_sensor_place_returns_correct_temperature_sensor_place(db_session_for_tests: Session):
    service = TemperatureSensorPlacesService(
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session_for_tests)
    )
    temperature_sensor_place_create = TemperatureSensorPlaceCreate(
        name="Test Temperature Sensor Place",
        temperature_sensor_place_type=TemperatureSensorPlaceType.APPLIANCE,
        location_id=uuid4(),
        temperature_sensor_id=uuid4()
    )
    service.create_temperature_sensor_place(
        TemperatureSensorPlaceCreate(
        name="Test Temperature Sensor Place 2",
        temperature_sensor_place_type=TemperatureSensorPlaceType.APPLIANCE,
        location_id=uuid4(),
        temperature_sensor_id=uuid4()
    )
    )
    temperature_sensor_place = service.create_temperature_sensor_place(temperature_sensor_place_create)
    temperature_sensor_place_model = service.get_temperature_sensor_place(temperature_sensor_place.temperature_sensor_place_id)
    assert temperature_sensor_place_model == temperature_sensor_place


def test_get_temperature_sensor_place_returns_none_if_temperature_sensor_place_not_found(db_session_for_tests: Session):
    service = TemperatureSensorPlacesService(
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session_for_tests)
    )
    temperature_sensor_place_create = TemperatureSensorPlaceCreate(
        name="Test Temperature Sensor Place",
        temperature_sensor_place_type=TemperatureSensorPlaceType.APPLIANCE,
        location_id=uuid4(),
        temperature_sensor_id=uuid4()
    )
    service.create_temperature_sensor_place(temperature_sensor_place_create)
    temperature_sensor_place_model = service.get_temperature_sensor_place(uuid4())
    assert temperature_sensor_place_model is None


def test_delete_temperature_sensor_place_removes_temperature_sensor_place_from_db(db_session_for_tests: Session):
    service = TemperatureSensorPlacesService(
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session_for_tests)
    )
    temperature_sensor_place_create = TemperatureSensorPlaceCreate(
        name="Test Temperature Sensor Place",
        temperature_sensor_place_type=TemperatureSensorPlaceType.APPLIANCE,
        location_id=uuid4(),
        temperature_sensor_id=uuid4()
    )
    temperature_sensor_place = service.create_temperature_sensor_place(temperature_sensor_place_create)
    service.delete_temperature_sensor_place(temperature_sensor_place.temperature_sensor_place_id)
    temperature_sensor_place_models = db_session_for_tests.query(TemperatureSensorPlace).all()
    assert len(temperature_sensor_place_models) == 0
