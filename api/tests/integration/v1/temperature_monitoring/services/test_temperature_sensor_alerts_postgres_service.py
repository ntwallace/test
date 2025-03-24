from datetime import datetime
from uuid import uuid4, UUID

import pytest

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.temperature_monitoring.models.temperature_sensor_place_alert import TemperatureSensorPlaceAlert as TemperatureSensorPlaceAlertModel
from app.v1.temperature_monitoring.repositories.temperature_sensor_place_alerts_repository import PostgresTemperatureSensorPlaceAlertsRepository
from app.v1.temperature_monitoring.repositories.temperature_sensor_places_repository import PostgresTemperatureSensorPlacesRepository
from app.v1.temperature_monitoring.schemas.temperature_sensor_place_alert import (
    TemperatureSensorPlaceAlertCreate,
    TemperatureSensorPlaceAlert,
    TemperatureSensorPlaceAlertType
)
from app.v1.temperature_monitoring.services.temperature_sensor_place_alerts import TemperatureSensorPlaceAlertsService


def test_create_temperature_sensor_alert_inserts_new_model(db_session_for_tests: Session):
    service = TemperatureSensorPlaceAlertsService(
        temperature_sensor_place_alerts_repository=PostgresTemperatureSensorPlaceAlertsRepository(db_session_for_tests),
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session_for_tests)
    )
    temperature_sensor_alert_create = TemperatureSensorPlaceAlertCreate(
        temperature_sensor_place_id=uuid4(),
        alert_type=TemperatureSensorPlaceAlertType.ABOVE_NORMAL_OPERATING_RANGE,
        threshold_temperature_c=20.0,
        threshold_window_seconds=300,
        reporter_temperature_c=25.0,
        started_at=datetime.now(),
        ended_at=None
    )
    temperature_sensor_alert = service.create_temperature_sensor_place_alert(temperature_sensor_alert_create)
    temperature_sensor_alert_models = db_session_for_tests.query(TemperatureSensorPlaceAlertModel).all()
    assert len(temperature_sensor_alert_models) == 1
    temperature_sensor_alert_model = temperature_sensor_alert_models[0]
    assert temperature_sensor_alert_model.temperature_sensor_place_alert_id == temperature_sensor_alert.temperature_sensor_place_alert_id
    assert temperature_sensor_alert_model.temperature_sensor_place_id == temperature_sensor_alert.temperature_sensor_place_id
    assert temperature_sensor_alert_model.alert_type == temperature_sensor_alert.alert_type
    assert temperature_sensor_alert_model.threshold_temperature_c == temperature_sensor_alert.threshold_temperature_c
    assert temperature_sensor_alert_model.threshold_window_seconds == temperature_sensor_alert.threshold_window_seconds
    assert temperature_sensor_alert_model.reporter_temperature_c == temperature_sensor_alert.reporter_temperature_c
    assert temperature_sensor_alert_model.started_at == temperature_sensor_alert.started_at
    assert temperature_sensor_alert_model.ended_at == temperature_sensor_alert.ended_at
    assert temperature_sensor_alert_model.created_at == temperature_sensor_alert.created_at
    assert temperature_sensor_alert_model.updated_at == temperature_sensor_alert.updated_at
    

def test_get_temperature_sensor_alerts_for_temperature_sensor_returns_correct_temperature_sensor_alerts(db_session_for_tests: Session):
    service = TemperatureSensorPlaceAlertsService(
        temperature_sensor_place_alerts_repository=PostgresTemperatureSensorPlaceAlertsRepository(db_session_for_tests),
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session_for_tests)
    )
    temperature_sensor_alert_create = TemperatureSensorPlaceAlertCreate(
        temperature_sensor_place_id=uuid4(),
        alert_type=TemperatureSensorPlaceAlertType.ABOVE_NORMAL_OPERATING_RANGE,
        threshold_temperature_c=20.0,
        threshold_window_seconds=300,
        reporter_temperature_c=25.0,
        started_at=datetime.now(),
        ended_at=None
    )
    temperature_sensor_alert = service.create_temperature_sensor_place_alert(temperature_sensor_alert_create)
    temperature_sensor_alerts = service.get_temperature_sensor_place_alerts_for_temperature_sensor_place(temperature_sensor_alert.temperature_sensor_place_id)
    assert len(temperature_sensor_alerts) == 1
    temperature_sensor_alert_schema = temperature_sensor_alerts[0]
    assert temperature_sensor_alert_schema.temperature_sensor_place_alert_id == temperature_sensor_alert.temperature_sensor_place_alert_id
    assert temperature_sensor_alert_schema.temperature_sensor_place_id == temperature_sensor_alert.temperature_sensor_place_id
    assert temperature_sensor_alert_schema.alert_type == temperature_sensor_alert.alert_type
    assert temperature_sensor_alert_schema.threshold_temperature_c == temperature_sensor_alert.threshold_temperature_c
    assert temperature_sensor_alert_schema.threshold_window_seconds == temperature_sensor_alert.threshold_window_seconds
    assert temperature_sensor_alert_schema.reporter_temperature_c == temperature_sensor_alert.reporter_temperature_c
    assert temperature_sensor_alert_schema.started_at == temperature_sensor_alert.started_at
    assert temperature_sensor_alert_schema.ended_at == temperature_sensor_alert.ended_at
    assert temperature_sensor_alert_schema.created_at == temperature_sensor_alert.created_at
    assert temperature_sensor_alert_schema.updated_at == temperature_sensor_alert.updated_at


def test_get_temperature_sensor_alerts_for_temperature_sensor_returns_empty_list_if_no_temperature_sensor_alerts_exist(db_session_for_tests: Session):
    service = TemperatureSensorPlaceAlertsService(
        temperature_sensor_place_alerts_repository=PostgresTemperatureSensorPlaceAlertsRepository(db_session_for_tests),
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session_for_tests)
    )
    temperature_sensor_alert_create = TemperatureSensorPlaceAlertCreate(
        temperature_sensor_place_id=uuid4(),
        alert_type=TemperatureSensorPlaceAlertType.ABOVE_NORMAL_OPERATING_RANGE,
        threshold_temperature_c=20.0,
        threshold_window_seconds=300,
        reporter_temperature_c=25.0,
        started_at=datetime.now(),
        ended_at=None
    )
    service.create_temperature_sensor_place_alert(temperature_sensor_alert_create)
    temperature_sensor_alerts = service.get_temperature_sensor_place_alerts_for_temperature_sensor_place(uuid4())
    assert len(temperature_sensor_alerts) == 0


def test_get_temperature_sensor_place_alert_for_temperature_sensor_place_returns_correct_temperature_sensor_alert(db_session_for_tests: Session):
    service = TemperatureSensorPlaceAlertsService(
        temperature_sensor_place_alerts_repository=PostgresTemperatureSensorPlaceAlertsRepository(db_session_for_tests),
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session_for_tests)
    )
    temperature_sensor_alert_create = TemperatureSensorPlaceAlertCreate(
        temperature_sensor_place_id=uuid4(),
        alert_type=TemperatureSensorPlaceAlertType.ABOVE_NORMAL_OPERATING_RANGE,
        threshold_temperature_c=20.0,
        threshold_window_seconds=300,
        reporter_temperature_c=25.0,
        started_at=datetime.now(),
        ended_at=None
    )
    temperature_sensor_alert = service.create_temperature_sensor_place_alert(temperature_sensor_alert_create)
    temperature_sensor_alert_schema = service.get_temperature_sensor_place_alert_for_temperature_sensor_place(temperature_sensor_alert.temperature_sensor_place_id, temperature_sensor_alert.temperature_sensor_place_alert_id)
    assert temperature_sensor_alert_schema.temperature_sensor_place_alert_id == temperature_sensor_alert.temperature_sensor_place_alert_id
    assert temperature_sensor_alert_schema.temperature_sensor_place_id == temperature_sensor_alert.temperature_sensor_place_id
    assert temperature_sensor_alert_schema.alert_type == temperature_sensor_alert.alert_type
    assert temperature_sensor_alert_schema.threshold_temperature_c == temperature_sensor_alert.threshold_temperature_c
    assert temperature_sensor_alert_schema.threshold_window_seconds == temperature_sensor_alert.threshold_window_seconds
    assert temperature_sensor_alert_schema.reporter_temperature_c == temperature_sensor_alert.reporter_temperature_c
    assert temperature_sensor_alert_schema.started_at == temperature_sensor_alert.started_at
    assert temperature_sensor_alert_schema.ended_at == temperature_sensor_alert.ended_at
    assert temperature_sensor_alert_schema.created_at == temperature_sensor_alert.created_at
    assert temperature_sensor_alert_schema.updated_at == temperature_sensor_alert.updated_at


def test_get_temperature_sensor_place_alert_for_temperature_sensor_place_when_temperature_sensor_alert_doesnt_exist(db_session_for_tests: Session):
    service = TemperatureSensorPlaceAlertsService(
        temperature_sensor_place_alerts_repository=PostgresTemperatureSensorPlaceAlertsRepository(db_session_for_tests),
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session_for_tests)
    )
    temperature_sensor_alert_create = TemperatureSensorPlaceAlertCreate(
        temperature_sensor_place_id=uuid4(),
        alert_type=TemperatureSensorPlaceAlertType.ABOVE_NORMAL_OPERATING_RANGE,
        threshold_temperature_c=20.0,
        threshold_window_seconds=300,
        reporter_temperature_c=25.0,
        started_at=datetime.now(),
        ended_at=None
    )
    service.create_temperature_sensor_place_alert(temperature_sensor_alert_create)
    temperature_sensor_alert_schema = service.get_temperature_sensor_place_alert_for_temperature_sensor_place(uuid4(), uuid4())
    assert temperature_sensor_alert_schema is None


def test_delete_temperature_sensor_alert_deletes_correct_temperature_sensor_alert(db_session_for_tests: Session):
    service = TemperatureSensorPlaceAlertsService(
        temperature_sensor_place_alerts_repository=PostgresTemperatureSensorPlaceAlertsRepository(db_session_for_tests),
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session_for_tests)
    )
    temperature_sensor_alert_create = TemperatureSensorPlaceAlertCreate(
        temperature_sensor_place_id=uuid4(),
        alert_type=TemperatureSensorPlaceAlertType.ABOVE_NORMAL_OPERATING_RANGE,
        threshold_temperature_c=20.0,
        threshold_window_seconds=300,
        reporter_temperature_c=25.0,
        started_at=datetime.now(),
        ended_at=None
    )
    temperature_sensor_alert = service.create_temperature_sensor_place_alert(temperature_sensor_alert_create)
    service.delete_temperature_sensor_place_alert(temperature_sensor_alert.temperature_sensor_place_alert_id)
    temperature_sensor_alerts = db_session_for_tests.query(TemperatureSensorPlaceAlertModel).all()
    assert len(temperature_sensor_alerts) == 0
