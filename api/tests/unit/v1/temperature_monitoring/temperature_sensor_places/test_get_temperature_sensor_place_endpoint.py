from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_temperature_sensor_places_service, get_access_token_data
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import TemperatureSensorPlace
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_get_temperature_sensor_place_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/temperature-sensor-places/{uuid4()}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.TEMPERATURE_MONITORING_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.TEMPERATURE_MONITORING_READ], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_get_temperature_sensor_place_access_scopes(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace,
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.get(f'/v1/temperature-sensor-places/{temperature_sensor_place.temperature_sensor_place_id}')

    assert response.status_code == response_code


def test_get_temperature_sensor_place_success_response(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.get(f'/v1/temperature-sensor-places/{temperature_sensor_place.temperature_sensor_place_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'temperature_sensor_place_id': str(temperature_sensor_place.temperature_sensor_place_id),
        'name': temperature_sensor_place.name,
        'temperature_sensor_place_type': temperature_sensor_place.temperature_sensor_place_type,
        'location_id': str(temperature_sensor_place.location_id),
        'temperature_sensor_id': str(temperature_sensor_place.temperature_sensor_id),
        'created_at': temperature_sensor_place.created_at.isoformat(),
        'updated_at': temperature_sensor_place.updated_at.isoformat()
    }


def test_get_temperature_sensor_place_when_temperature_sensor_places_dont_exist(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = None
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.get(f'/v1/temperature-sensor-places/{uuid4()}')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_temperature_sensor_place_when_location_is_unauthorized(
    no_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace
):
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data

    temperature_sensor_place.location_id = uuid4()
    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.get(f'/v1/temperature-sensor-places/{temperature_sensor_place.temperature_sensor_place_id}')

    assert response.status_code == status.HTTP_403_FORBIDDEN
