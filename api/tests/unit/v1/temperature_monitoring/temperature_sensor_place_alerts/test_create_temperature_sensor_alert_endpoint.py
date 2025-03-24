from datetime import datetime
from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.v1.dependencies import get_temperature_sensor_place_alerts_service, get_temperature_sensor_places_service, get_access_token_data, get_user_location_access_grants_service, get_user_access_grants_helper
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import TemperatureSensorPlace
from app.v1.temperature_monitoring.schemas.temperature_sensor_place_alert import TemperatureSensorPlaceAlert
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_create_temperature_sensor_place_alert_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post(f'/v1/temperature-sensor-places/{uuid4()}/alerts')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.TEMPERATURE_MONITORING_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.TEMPERATURE_MONITORING_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_temperature_sensor_place_alert_access_scopes(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place_alerts_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace,
    temperature_sensor_place_alert: TemperatureSensorPlaceAlert,
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    temperature_sensor_place_alerts_service_mock.create_temperature_sensor_place_alert.return_value = temperature_sensor_place_alert
    app.dependency_overrides[get_temperature_sensor_place_alerts_service] = lambda: temperature_sensor_place_alerts_service_mock

    response = test_client.post(f'/v1/temperature-sensor-places/{temperature_sensor_place_alert.temperature_sensor_place_id}/alerts', json={
        'temperature_sensor_place_id': str(temperature_sensor_place_alert.temperature_sensor_place_id),
        'alert_type': temperature_sensor_place_alert.alert_type,
        'threshold_temperature_c': temperature_sensor_place_alert.threshold_temperature_c,
        'threshold_window_seconds': temperature_sensor_place_alert.threshold_window_seconds,
        'reporter_temperature_c': temperature_sensor_place_alert.reporter_temperature_c,
        'started_at': temperature_sensor_place_alert.started_at.isoformat(),
        'ended_at': temperature_sensor_place_alert.ended_at.isoformat() if temperature_sensor_place_alert.ended_at else None
    })

    assert response.status_code == response_code


def test_create_temperature_sensor_place_alert_success_response(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_place_alerts_service_mock: Mock,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place_alert: TemperatureSensorPlaceAlert
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    temperature_sensor_place_alerts_service_mock.create_temperature_sensor_place_alert.return_value = temperature_sensor_place_alert
    app.dependency_overrides[get_temperature_sensor_place_alerts_service] = lambda: temperature_sensor_place_alerts_service_mock

    response = test_client.post(f'/v1/temperature-sensor-places/{uuid4()}/alerts', json={
        'temperature_sensor_place_id': str(temperature_sensor_place_alert.temperature_sensor_place_id),
        'alert_type': temperature_sensor_place_alert.alert_type,
        'threshold_temperature_c': temperature_sensor_place_alert.threshold_temperature_c,
        'threshold_window_seconds': temperature_sensor_place_alert.threshold_window_seconds,
        'reporter_temperature_c': temperature_sensor_place_alert.reporter_temperature_c,
        'started_at': temperature_sensor_place_alert.started_at.isoformat(),
        'ended_at': temperature_sensor_place_alert.ended_at.isoformat() if temperature_sensor_place_alert.ended_at else None
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'temperature_sensor_place_alert_id': str(temperature_sensor_place_alert.temperature_sensor_place_alert_id),
        'temperature_sensor_place_id': str(temperature_sensor_place_alert.temperature_sensor_place_id),
        'alert_type': temperature_sensor_place_alert.alert_type,
        'threshold_temperature_c': temperature_sensor_place_alert.threshold_temperature_c,
        'threshold_window_seconds': temperature_sensor_place_alert.threshold_window_seconds,
        'reporter_temperature_c': temperature_sensor_place_alert.reporter_temperature_c,
        'started_at': temperature_sensor_place_alert.started_at.isoformat(),
        'ended_at': temperature_sensor_place_alert.ended_at.isoformat() if temperature_sensor_place_alert.ended_at else None,
        'created_at': temperature_sensor_place_alert.created_at.isoformat(),
        'updated_at': temperature_sensor_place_alert.updated_at.isoformat()
    }


def test_create_temperature_sensor_place_alert_when_temperature_sensor_place_alert_exists(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_place_alerts_service_mock: Mock,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place_alert: TemperatureSensorPlaceAlert
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    temperature_sensor_place_alerts_service_mock.create_temperature_sensor_place_alert.side_effect = IntegrityError(None, None, None)
    app.dependency_overrides[get_temperature_sensor_place_alerts_service] = lambda: temperature_sensor_place_alerts_service_mock

    response = test_client.post(f'/v1/temperature-sensor-places/{uuid4()}/alerts', json={
        'temperature_sensor_place_id': str(temperature_sensor_place_alert.temperature_sensor_place_id),
        'alert_type': temperature_sensor_place_alert.alert_type,
        'threshold_temperature_c': temperature_sensor_place_alert.threshold_temperature_c,
        'threshold_window_seconds': temperature_sensor_place_alert.threshold_window_seconds,
        'reporter_temperature_c': temperature_sensor_place_alert.reporter_temperature_c,
        'started_at': temperature_sensor_place_alert.started_at.isoformat(),
        'ended_at': temperature_sensor_place_alert.ended_at.isoformat() if temperature_sensor_place_alert.ended_at else None
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_temperature_sensor_place_alert_when_temperature_sensor_does_not_exist(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_place_alerts_service_mock: Mock,
    temperature_sensor_places_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = None
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    app.dependency_overrides[get_temperature_sensor_place_alerts_service] = lambda: temperature_sensor_place_alerts_service_mock

    temperature_sensor_place_id = uuid4()
    response = test_client.post(f'/v1/temperature-sensor-places/{temperature_sensor_place_id}/alerts', json={
        'temperature_sensor_place_id': str(temperature_sensor_place_id),
        'alert_type': 'ABOVE_NORMAL_OPERATING_RANGE',
        'threshold_temperature_c': 20.0,
        'threshold_window_seconds': 300,
        'reporter_temperature_c': 25.0,
        'started_at': datetime.now().isoformat(),
        'ended_at': None
    })

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_temperature_sensor_place_alert_when_temperature_sensor_is_unauthorized(
    all_access_token_data: AccessTokenData,
    temperature_sensor_place_alerts_service_mock: Mock,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place_alert: TemperatureSensorPlaceAlert,
    temperature_sensor_place: TemperatureSensorPlace,
    user_access_grants_helper_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: all_access_token_data
    user_access_grants_helper_mock.is_user_authorized_for_location_read.return_value = False
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    temperature_sensor_place.location_id = uuid4()
    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    app.dependency_overrides[get_temperature_sensor_place_alerts_service] = lambda: temperature_sensor_place_alerts_service_mock

    response = test_client.post(f'/v1/temperature-sensor-places/{temperature_sensor_place_alert.temperature_sensor_place_id}/alerts', json={
        'temperature_sensor_place_id': str(temperature_sensor_place_alert.temperature_sensor_place_id),
        'alert_type': temperature_sensor_place_alert.alert_type,
        'threshold_temperature_c': temperature_sensor_place_alert.threshold_temperature_c,
        'threshold_window_seconds': temperature_sensor_place_alert.threshold_window_seconds,
        'reporter_temperature_c': temperature_sensor_place_alert.reporter_temperature_c,
        'started_at': temperature_sensor_place_alert.started_at.isoformat(),
        'ended_at': temperature_sensor_place_alert.ended_at.isoformat() if temperature_sensor_place_alert.ended_at else None
    })

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_temperature_sensor_place_alert_when_temperature_sensor_place_id_is_mismatched(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_place_alerts_service_mock: Mock,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place_alert: TemperatureSensorPlaceAlert
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock
    app.dependency_overrides[get_temperature_sensor_place_alerts_service] = lambda: temperature_sensor_place_alerts_service_mock

    response = test_client.post(f'/v1/temperature-sensor-places/{temperature_sensor_place_alert.temperature_sensor_place_id}/alerts', json={
        'temperature_sensor_place_id': str(uuid4()),
        'alert_type': temperature_sensor_place_alert.alert_type,
        'threshold_temperature_c': temperature_sensor_place_alert.threshold_temperature_c,
        'threshold_window_seconds': temperature_sensor_place_alert.threshold_window_seconds,
        'reporter_temperature_c': temperature_sensor_place_alert.reporter_temperature_c,
        'started_at': temperature_sensor_place_alert.started_at.isoformat(),
        'ended_at': temperature_sensor_place_alert.ended_at.isoformat() if temperature_sensor_place_alert.ended_at else None
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST


