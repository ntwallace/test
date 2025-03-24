from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import get_api_key_access_scopes_helper, get_api_key_data, get_temperature_sensor_places_service, get_access_token_data
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import TemperatureSensorPlace
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_create_temperature_sensor_place_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post('/v1/temperature-sensor-places')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.TEMPERATURE_MONITORING_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.TEMPERATURE_MONITORING_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.TEMPERATURE_MONITORING_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_temperature_sensor_place_access_scopes(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    temperature_sensor_places_service_mock.create_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.post('/v1/temperature-sensor-places', json={
        'name': temperature_sensor_place.name,
        'temperature_sensor_place_type': temperature_sensor_place.temperature_sensor_place_type,
        'location_id': str(temperature_sensor_place.location_id),
        'temperature_sensor_id': str(temperature_sensor_place.temperature_sensor_id)
    })

    assert response.status_code == response_code


def test_create_temperature_sensor_place_success_response(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.create_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.post('/v1/temperature-sensor-places', json={
        'name': temperature_sensor_place.name,
        'temperature_sensor_place_type': temperature_sensor_place.temperature_sensor_place_type,
        'location_id': str(temperature_sensor_place.location_id),
        'temperature_sensor_id': str(temperature_sensor_place.temperature_sensor_id)
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'temperature_sensor_place_id': str(temperature_sensor_place.temperature_sensor_place_id),
        'temperature_sensor_place_type': temperature_sensor_place.temperature_sensor_place_type,
        'name': temperature_sensor_place.name,
        'location_id': str(temperature_sensor_place.location_id),
        'temperature_sensor_id': str(temperature_sensor_place.temperature_sensor_id),
        'created_at': temperature_sensor_place.created_at.isoformat(),
        'updated_at': temperature_sensor_place.updated_at.isoformat()
    }


def test_create_temperature_sensor_place_when_temperature_sensor_place_exists(
    admin_all_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    temperature_sensor_places_service_mock.create_temperature_sensor_place.side_effect = IntegrityError(None, None, None)
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.post('/v1/temperature-sensor-places', json={
        'name': temperature_sensor_place.name,
        'temperature_sensor_place_type': temperature_sensor_place.temperature_sensor_place_type,
        'location_id': str(temperature_sensor_place.location_id),
        'temperature_sensor_id': str(temperature_sensor_place.temperature_sensor_id)
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_temperature_sensor_place_when_location_is_unauthorized(
    no_access_token_data: AccessTokenData,
    temperature_sensor_places_service_mock: Mock,
    temperature_sensor_place: TemperatureSensorPlace
):
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data

    temperature_sensor_place.location_id = uuid4()
    temperature_sensor_places_service_mock.create_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.post('/v1/temperature-sensor-places', json={
        'name': temperature_sensor_place.name,
        'temperature_sensor_place_type': temperature_sensor_place.temperature_sensor_place_type,
        'location_id': str(temperature_sensor_place.location_id),
        'temperature_sensor_id': str(temperature_sensor_place.temperature_sensor_id)
    })

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_temperature_sensor_place_using_api_key_auth(
    api_key: APIKey,
    temperature_sensor_place: TemperatureSensorPlace,
    api_key_access_scopes_helper_mock: Mock,
    temperature_sensor_places_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: None
    app.dependency_overrides[get_api_key_data] = lambda: api_key

    api_key_access_scopes_helper_mock.get_all_access_scopes_for_api_key.return_value = [AccessScope.ADMIN, AccessScope.TEMPERATURE_MONITORING_WRITE]
    app.dependency_overrides[get_api_key_access_scopes_helper] = lambda: api_key_access_scopes_helper_mock

    temperature_sensor_places_service_mock.create_temperature_sensor_place.return_value = temperature_sensor_place
    app.dependency_overrides[get_temperature_sensor_places_service] = lambda: temperature_sensor_places_service_mock

    response = test_client.post('/v1/temperature-sensor-places', json={
        'name': 'name',
        'temperature_sensor_place_type': 'appliance',
        'location_id': str(uuid4()),
        'temperature_sensor_id': str(uuid4())
    })

    assert response.status_code == status.HTTP_201_CREATED