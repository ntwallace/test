from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.v1.dependencies import get_hvac_zone_temperature_sensors_service, get_hvac_zones_service, get_temperature_sensors_service, get_access_token_data
from app.v1.hvac.schemas.hvac_zone_temperature_sensor import HvacZoneTemperatureSensor
from app.v1.hvac.schemas.hvac_zone import HvacZone
from app.v1.temperature_monitoring.schemas.temperature_sensor import TemperatureSensor
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_create_hvac_zone_temperature_sensor_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post('/v1/hvac-zone-temperature-sensors')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.HVAC_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.HVAC_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.HVAC_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_hvac_zone_temperature_sensor_access_scopes(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    hvac_zone_temperature_sensors_service_mock: Mock,
    hvac_zone_temperature_sensor: HvacZoneTemperatureSensor,
    hvac_zones_service_mock: Mock,
    hvac_zone: HvacZone,
    temperature_sensor: TemperatureSensor,
    temperature_sensors_service_mock: Mock
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    hvac_zone_temperature_sensors_service_mock.create_hvac_zone_temperature_sensor.return_value =  hvac_zone_temperature_sensor
    app.dependency_overrides[get_hvac_zone_temperature_sensors_service] = lambda:  hvac_zone_temperature_sensors_service_mock

    hvac_zones_service_mock.get_hvac_zone_by_id.return_value = hvac_zone
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock

    temperature_sensors_service_mock.get_temperature_sensor_by_id.return_value = temperature_sensor
    app.dependency_overrides[get_temperature_sensors_service] = lambda: temperature_sensors_service_mock

    response = test_client.post('/v1/hvac-zone-temperature-sensors', json={
        'hvac_zone_id': str(hvac_zone_temperature_sensor.hvac_zone_id),
        'temperature_sensor_id': str(hvac_zone_temperature_sensor.temperature_sensor_id)
    })

    assert response.status_code == response_code


def test_create_hvac_zone_temperature_sensor_success_response(
    admin_all_access_token_data: AccessTokenData,
    hvac_zone_temperature_sensors_service_mock: Mock,
    hvac_zone_temperature_sensor: HvacZoneTemperatureSensor,
    hvac_zones_service_mock: Mock,
    hvac_zone: HvacZone,
    temperature_sensor: TemperatureSensor,
    temperature_sensors_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    hvac_zone_temperature_sensors_service_mock.create_hvac_zone_temperature_sensor.return_value =  hvac_zone_temperature_sensor
    app.dependency_overrides[get_hvac_zone_temperature_sensors_service] = lambda:  hvac_zone_temperature_sensors_service_mock

    hvac_zones_service_mock.get_hvac_zone_by_id.return_value = hvac_zone
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock

    temperature_sensors_service_mock.get_temperature_sensor_by_id.return_value = temperature_sensor
    app.dependency_overrides[get_temperature_sensors_service] = lambda: temperature_sensors_service_mock

    response = test_client.post('/v1/hvac-zone-temperature-sensors', json={
        'hvac_zone_id': str(hvac_zone_temperature_sensor.hvac_zone_id),
        'temperature_sensor_id': str(hvac_zone_temperature_sensor.temperature_sensor_id)
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'hvac_zone_id': str(hvac_zone_temperature_sensor.hvac_zone_id),
        'temperature_sensor_id': str(hvac_zone_temperature_sensor.temperature_sensor_id),
        'hvac_zone_temperature_sensor_id': str(hvac_zone_temperature_sensor.hvac_zone_temperature_sensor_id),
        'created_at': hvac_zone_temperature_sensor.created_at.isoformat(),
        'updated_at': hvac_zone_temperature_sensor.updated_at.isoformat()
    }


def test_create_hvac_zone_temperature_sensor_when_temperature_sensor_exists(
    admin_all_access_token_data: AccessTokenData,
    hvac_zone_temperature_sensors_service_mock: Mock,
    hvac_zone_temperature_sensor: HvacZoneTemperatureSensor,
    hvac_zones_service_mock: Mock,
    hvac_zone: HvacZone,
    temperature_sensor: TemperatureSensor,
    temperature_sensors_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    hvac_zone_temperature_sensors_service_mock.create_hvac_zone_temperature_sensor.side_effect = IntegrityError(None, None, None)
    app.dependency_overrides[get_hvac_zone_temperature_sensors_service] = lambda:  hvac_zone_temperature_sensors_service_mock

    hvac_zones_service_mock.get_hvac_zone_by_id.return_value = hvac_zone
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock

    temperature_sensors_service_mock.get_temperature_sensor_by_id.return_value = temperature_sensor
    app.dependency_overrides[get_temperature_sensors_service] = lambda: temperature_sensors_service_mock

    response = test_client.post('/v1/hvac-zone-temperature-sensors', json={
        'hvac_zone_id': str(hvac_zone_temperature_sensor.hvac_zone_id),
        'temperature_sensor_id': str(hvac_zone_temperature_sensor.temperature_sensor_id)
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
