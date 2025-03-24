from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_temperature_ranges_service, get_access_token_data, get_temperature_sensor_places_service
from app.v1.temperature_monitoring.schemas.temperature_range import TemperatureRange
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import TemperatureSensorPlace


test_client = TestClient(app)


def test_get_temperature_range_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/temperature-sensor-places/{uuid4()}/temperature-ranges/{uuid4()}')
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
def test_get_temperature_range_access_scopes(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    temperature_sensor_places_service_mock: Mock,
    temperature_ranges_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace,
    temperature_range: TemperatureRange
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    temperature_ranges_service_mock.get_temperature_range_for_temperature_sensor_place_by_id.return_value = temperature_range
    app.dependency_overrides[get_temperature_ranges_service] = lambda: temperature_ranges_service_mock

    response = test_client.get(f'/v1/temperature-sensor-places/{temperature_sensor_place.temperature_sensor_place_id}/temperature-ranges/{temperature_range.temperature_range_id}')

    assert response.status_code == response_code


def test_get_temperature_range_success_response(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_ranges_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace,
    temperature_range: TemperatureRange
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    temperature_ranges_service_mock.get_temperature_range_for_temperature_sensor_place_by_id.return_value = temperature_range
    app.dependency_overrides[get_temperature_ranges_service] = lambda: temperature_ranges_service_mock

    response = test_client.get(f'/v1/temperature-sensor-places/{temperature_sensor_place.temperature_sensor_place_id}/temperature-ranges/{temperature_range.temperature_range_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'temperature_range_id': str(temperature_range.temperature_range_id),
        'high_degrees_celcius': temperature_range.high_degrees_celcius,
        'low_degrees_celcius': temperature_range.low_degrees_celcius,
        'warning_level': temperature_range.warning_level,
        'temperature_sensor_place_id': str(temperature_range.temperature_sensor_place_id),
        'created_at': temperature_range.created_at.isoformat(),
        'updated_at': temperature_range.updated_at.isoformat()
    }


def test_get_temperature_range_when_temperature_range_dont_exist(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_ranges_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    temperature_ranges_service_mock.get_temperature_range_for_temperature_sensor_place_by_id.return_value = None
    app.dependency_overrides[get_temperature_ranges_service] = lambda: temperature_ranges_service_mock

    response = test_client.get(f'/v1/temperature-sensor-places/{temperature_sensor_place.temperature_sensor_place_id}/temperature-ranges/{uuid4()}')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_temperature_range_when_temperature_sensor_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_ranges_service_mock: Mock,
    temperature_range: TemperatureRange
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = None
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    temperature_ranges_service_mock.get_temperature_range_for_temperature_sensor_place_by_id.return_value = temperature_range
    app.dependency_overrides[get_temperature_ranges_service] = lambda: temperature_ranges_service_mock

    response = test_client.get(f'/v1/temperature-sensor-places/{uuid4()}/temperature-ranges/{temperature_range.temperature_range_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_temperature_range_when_temperature_sensor_is_unauthorized(
    no_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_ranges_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace,
    temperature_range: TemperatureRange
):
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data

    temperature_sensor_place.location_id = uuid4()
    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    temperature_ranges_service_mock.get_temperature_range_for_temperature_sensor_place_by_id.return_value = temperature_range
    app.dependency_overrides[get_temperature_ranges_service] = lambda: temperature_ranges_service_mock
    
    response = test_client.get(f'/v1/temperature-sensor-places/{temperature_sensor_place.temperature_sensor_place_id}/temperature-ranges/{temperature_range.temperature_range_id}')

    assert response.status_code == status.HTTP_403_FORBIDDEN
