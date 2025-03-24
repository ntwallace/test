from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_temperature_sensor_place_alerts_service, get_access_token_data, get_temperature_sensor_places_service
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import TemperatureSensorPlace
from app.v1.temperature_monitoring.schemas.temperature_sensor_place_alert import TemperatureSensorPlaceAlert
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_delete_temperature_sensor_place_alert_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.delete(f'/v1/temperature-sensor-places/{uuid4()}/alerts/{uuid4()}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.TEMPERATURE_MONITORING_WRITE], status.HTTP_204_NO_CONTENT),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.TEMPERATURE_MONITORING_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.TEMPERATURE_MONITORING_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_delete_temperature_sensor_place_alert_access_scopes(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place_alerts_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace,
    temperature_sensor_place_alert: TemperatureSensorPlaceAlert
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    temperature_sensor_place_alerts_service_mock.get_temperature_sensor_place_alert_for_temperature_sensor_place.return_value = temperature_sensor_place_alert
    temperature_sensor_place_alerts_service_mock.delete_temperature_sensor_place_alert.return_value = None
    app.dependency_overrides[get_temperature_sensor_place_alerts_service] = lambda: temperature_sensor_place_alerts_service_mock

    response = test_client.delete(f'/v1/temperature-sensor-places/{temperature_sensor_place.temperature_sensor_place_id}/alerts/{temperature_sensor_place_alert.temperature_sensor_place_alert_id}')
    assert response.status_code == response_code


def test_delete_temperature_sensor_place_alert_success_response(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place_alerts_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace,
    temperature_sensor_place_alert: TemperatureSensorPlaceAlert
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    temperature_sensor_place_alerts_service_mock.get_temperature_sensor_place_alert_for_temperature_sensor_place.return_value = temperature_sensor_place_alert
    app.dependency_overrides[get_temperature_sensor_place_alerts_service] = lambda: temperature_sensor_place_alerts_service_mock

    response = test_client.delete(f'/v1/temperature-sensor-places/{temperature_sensor_place.temperature_sensor_place_id}/alerts/{temperature_sensor_place_alert.temperature_sensor_place_alert_id}')
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_temperature_sensor_place_alert_when_no_alert_exists(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place_alerts_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    temperature_sensor_place_alerts_service_mock.get_temperature_sensor_place_alert_for_temperature_sensor_place.return_value = None
    app.dependency_overrides[get_temperature_sensor_place_alerts_service] = lambda: temperature_sensor_place_alerts_service_mock

    response = test_client.delete(f'/v1/temperature-sensor-places/{temperature_sensor_place.temperature_sensor_place_id}/alerts/{uuid4()}')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_temperature_sensor_place_alert_when_temperature_sensor_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place_alert: TemperatureSensorPlaceAlert
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = None
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.delete(f'/v1/temperature-sensor-places/{uuid4()}/alerts/{temperature_sensor_place_alert.temperature_sensor_place_alert_id}')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_temperature_sensor_place_alert_when_temperature_sensor_is_unauthorized(
    read_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace,
    temperature_sensor_place_alert: TemperatureSensorPlaceAlert
):
    app.dependency_overrides[get_access_token_data] = lambda: read_access_token_data

    temperature_sensor_place.location_id = uuid4()
    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.delete(f'/v1/temperature-sensor-places/{temperature_sensor_place.temperature_sensor_place_id}/alerts/{temperature_sensor_place_alert.temperature_sensor_place_alert_id}')
    assert response.status_code == status.HTTP_403_FORBIDDEN
