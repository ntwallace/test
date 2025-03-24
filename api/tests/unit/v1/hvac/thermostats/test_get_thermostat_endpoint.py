from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_thermostats_service, get_hvac_zones_service, get_access_token_data
from app.v1.hvac.schemas.thermostat import Thermostat
from app.v1.hvac.schemas.hvac_zone import HvacZone
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_get_thermostat_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/thermostats/{uuid4()}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.HVAC_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.HVAC_READ], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_get_thermostat_access_scopes(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    thermostats_service_mock: Mock,
    hvac_zones_service_mock: Mock,
    thermostat: Thermostat,
    hvac_zone: HvacZone
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    thermostats_service_mock.get_thermostat_by_id.return_value = thermostat
    app.dependency_overrides[get_thermostats_service] = lambda: thermostats_service_mock

    hvac_zones_service_mock.get_hvac_zone_by_id.return_value = hvac_zone
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock

    response = test_client.get(f'/v1/thermostats/{thermostat.thermostat_id}')

    assert response.status_code == response_code


def test_get_thermostat_success_response(
    admin_all_access_token_data: AccessTokenData,
    thermostats_service_mock: Mock,
    thermostat: Thermostat,
    hvac_zone: HvacZone,
    hvac_zones_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    thermostats_service_mock.get_thermostat_by_id.return_value = thermostat
    app.dependency_overrides[get_thermostats_service] = lambda: thermostats_service_mock

    hvac_zones_service_mock.get_hvac_zone_by_id.return_value = hvac_zone
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock

    response = test_client.get(f'/v1/thermostats/{thermostat.thermostat_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'thermostat_id': str(thermostat.thermostat_id),
        'name': thermostat.name,
        'duid': thermostat.duid,
        'modbus_address': thermostat.modbus_address,
        'model': thermostat.model.value,
        'node_id': str(thermostat.node_id),
        'hvac_zone_id': str(thermostat.hvac_zone_id),
        'fan_mode': thermostat.fan_mode.value,
        'keypad_lockout': thermostat.keypad_lockout.value,
        'created_at': thermostat.created_at.isoformat(),
        'updated_at': thermostat.updated_at.isoformat()
    }


def test_get_thermostat_when_thermostat_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    thermostats_service_mock: Mock,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    thermostats_service_mock.get_thermostat_by_id.return_value = None
    app.dependency_overrides[get_thermostats_service] = lambda: thermostats_service_mock

    response = test_client.get(f'/v1/thermostats/{uuid4()}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
