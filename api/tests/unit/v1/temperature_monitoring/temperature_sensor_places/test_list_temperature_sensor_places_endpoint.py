from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_temperature_sensor_places_service, get_access_token_data
from app.v1.locations.schemas.location import Location
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import TemperatureSensorPlace
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_list_temperature_sensor_places_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/temperature-sensor-places?location_id={uuid4()}')
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
def test_list_temperature_sensor_places_access_scopes(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace,
    location: Location
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    temperature_sensor_places_service_mock.filter_by.return_value = [temperature_sensor_place,]
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.get(f'/v1/temperature-sensor-places?location_id={location.location_id}')

    assert response.status_code == response_code


def test_list_temperature_sensor_places_success_response(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace,
    location: Location
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.filter_by.return_value = [temperature_sensor_place,]
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.get(f'/v1/temperature-sensor-places?location_id={location.location_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'temperature_sensor_place_id': str(temperature_sensor_place.temperature_sensor_place_id),
        'name': temperature_sensor_place.name,
        'temperature_sensor_place_type': temperature_sensor_place.temperature_sensor_place_type,
        'location_id': str(temperature_sensor_place.location_id),
        'temperature_sensor_id': str(temperature_sensor_place.temperature_sensor_id),
        'created_at': temperature_sensor_place.created_at.isoformat(),
        'updated_at': temperature_sensor_place.updated_at.isoformat()
    }]


def test_list_temperature_sensor_places_when_temperature_sensor_places_dont_exist(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    location: Location
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.get(f'/v1/temperature-sensor-places?location_id={location.location_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_temperature_sensor_places_when_location_is_unauthorized(
    no_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace
):
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data

    temperature_sensor_place.location_id = uuid4()
    temperature_sensor_places_service_mock.filter_by.return_value = [temperature_sensor_place,]
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.get(f'/v1/temperature-sensor-places?location_id={uuid4()}')

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_list_temperature_sensor_places_parses_query_params(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace,
    location: Location
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.filter_by.return_value = [temperature_sensor_place,]
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.get(f'/v1/temperature-sensor-places?location_id={location.location_id}&temperature_sensor_id={temperature_sensor_place.temperature_sensor_id}&name={temperature_sensor_place.name}')

    assert response.status_code == status.HTTP_200_OK
    assert temperature_sensor_places_service_mock.filter_by.call_args.kwargs == {
        'location_id': location.location_id,
        'temperature_sensor_id': temperature_sensor_place.temperature_sensor_id,
        'name': temperature_sensor_place.name
    }
    assert response.json() == [{
        'temperature_sensor_place_id': str(temperature_sensor_place.temperature_sensor_place_id),
        'name': temperature_sensor_place.name,
        'temperature_sensor_place_type': temperature_sensor_place.temperature_sensor_place_type,
        'location_id': str(temperature_sensor_place.location_id),
        'temperature_sensor_id': str(temperature_sensor_place.temperature_sensor_id),
        'created_at': temperature_sensor_place.created_at.isoformat(),
        'updated_at': temperature_sensor_place.updated_at.isoformat()
    }]
