from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_temperature_sensors_service, get_access_token_data
from app.v1.temperature_monitoring.schemas.temperature_sensor import TemperatureSensor
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_delete_temperature_sensor_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.delete(f'/v1/temperature-sensors/{uuid4()}')
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
def test_delete_temperature_sensor_access_scopes(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    temperature_sensors_service_mock: Mock,
    temperature_sensor: TemperatureSensor,
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    temperature_sensors_service_mock.get_temperature_sensor_by_id.return_value = temperature_sensor
    temperature_sensors_service_mock.delete_temperature_sensor.return_value = None
    app.dependency_overrides[get_temperature_sensors_service] = lambda: temperature_sensors_service_mock

    response = test_client.delete(f'/v1/temperature-sensors/{temperature_sensor.temperature_sensor_id}')

    assert response.status_code == response_code


def test_delete_temperature_sensor_success_response(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensors_service_mock: Mock,
    temperature_sensor: TemperatureSensor,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensors_service_mock.get_temperature_sensor_by_id.return_value = temperature_sensor
    temperature_sensors_service_mock.delete_temperature_sensor.return_value = None
    app.dependency_overrides[get_temperature_sensors_service] = lambda: temperature_sensors_service_mock

    response = test_client.delete(f'/v1/temperature-sensors/{temperature_sensor.temperature_sensor_id}')

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_temperature_sensor_when_temperature_sensors_dont_exist(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensors_service_mock: Mock,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensors_service_mock.get_temperature_sensor_by_id.return_value = None
    app.dependency_overrides[get_temperature_sensors_service] = lambda: temperature_sensors_service_mock

    response = test_client.delete(f'/v1/temperature-sensors/{uuid4()}')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_temperature_sensor_when_location_is_unauthorized(
    no_access_token_data: AccessTokenData,
    temperature_sensors_service_mock: Mock,
    temperature_sensor: TemperatureSensor
):
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data

    temperature_sensor.location_id = uuid4()
    temperature_sensors_service_mock.get_temperature_sensor_by_id.return_value = temperature_sensor
    app.dependency_overrides[get_temperature_sensors_service] = lambda: temperature_sensors_service_mock

    response = test_client.delete(f'/v1/temperature-sensors/{temperature_sensor.temperature_sensor_id}')

    assert response.status_code == status.HTTP_403_FORBIDDEN
