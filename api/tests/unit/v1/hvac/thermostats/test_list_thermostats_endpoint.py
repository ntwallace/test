from datetime import datetime
from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4
import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import get_access_token_data, get_api_key_access_scopes_helper, get_api_key_data, get_hvac_zones_service, get_locations_service, get_thermostats_service, get_user_access_grants_helper
from app.v1.hvac.schemas.thermostat import Thermostat, ThermostatHvacFanMode, ThermostatLockoutType, ThermostatModelEnum
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_list_thermostats_is_unauthorized_without_token():
    response = test_client.get('/v1/thermostats')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([], status.HTTP_403_FORBIDDEN),
        ([AccessScope.HVAC_READ], status.HTTP_200_OK),
        ([AccessScope.HVAC_WRITE], status.HTTP_403_FORBIDDEN),
    ]
)
def test_list_thermostats_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    thermostats_service_mock: Mock,
    hvac_zones_service_mock: Mock,
    locations_service_mock: Mock,
    user_access_grants_helper_mock: Mock
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    user_access_grants_helper_mock.is_user_authorized_for_location_read.return_value = True
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock
    app.dependency_overrides[get_thermostats_service] = lambda: thermostats_service_mock

    response = test_client.get('/v1/thermostats')

    assert response.status_code == response_code


def test_list_thermostats_success_response_when_jwt_auth(
    thermostat: Thermostat,
    token_data_with_access_scopes: Callable,
    thermostats_service_mock: Mock,
    hvac_zones_service_mock: Mock,
    locations_service_mock: Mock,
    user_access_grants_helper_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.HVAC_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    user_access_grants_helper_mock.is_user_authorized_for_location_read.return_value = True
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    thermostats_service_mock.filter_by.return_value = [thermostat, ]
    app.dependency_overrides[get_thermostats_service] = lambda: thermostats_service_mock
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get('/v1/thermostats')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'thermostat_id': str(thermostat.thermostat_id),
        'name': thermostat.name,
        'duid': thermostat.duid,
        'modbus_address': thermostat.modbus_address,
        'model': thermostat.model,
        'node_id': str(thermostat.node_id),
        'hvac_zone_id': str(thermostat.hvac_zone_id),
        'keypad_lockout': thermostat.keypad_lockout,
        'fan_mode': thermostat.fan_mode,
        'created_at': thermostat.created_at.isoformat(),
        'updated_at': thermostat.updated_at.isoformat()
    }]


def test_list_thermostats_success_response_when_api_key_auth(
    api_key: APIKey,
    thermostat: Thermostat,
    api_key_access_scopes_helper_mock: Mock,
    thermostats_service_mock: Mock,
    hvac_zones_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_api_key_data] = lambda: api_key
    api_key_access_scopes_helper_mock.get_all_access_scopes_for_api_key.return_value = [AccessScope.HVAC_READ, AccessScope.ADMIN]
    app.dependency_overrides[get_api_key_access_scopes_helper] = lambda: api_key_access_scopes_helper_mock

    thermostats_service_mock.filter_by.return_value = [thermostat, ]
    app.dependency_overrides[get_thermostats_service] = lambda: thermostats_service_mock
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get('/v1/thermostats')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'thermostat_id': str(thermostat.thermostat_id),
        'name': thermostat.name,
        'duid': thermostat.duid,
        'modbus_address': thermostat.modbus_address,
        'model': str(thermostat.model),
        'node_id': str(thermostat.node_id),
        'hvac_zone_id': str(thermostat.hvac_zone_id),
        'keypad_lockout': str(thermostat.keypad_lockout),
        'fan_mode': str(thermostat.fan_mode),
        'created_at': thermostat.created_at.isoformat(),
        'updated_at': thermostat.updated_at.isoformat()
    }]


def test_list_thermostats_empty_response(
    token_data_with_access_scopes: Callable,
    thermostats_service_mock: Mock,
    hvac_zones_service_mock: Mock,
    locations_service_mock: Mock,
    user_access_grants_helper_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.HVAC_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    user_access_grants_helper_mock.is_user_authorized_for_location_read.return_value = True
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    thermostats_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_thermostats_service] = lambda: thermostats_service_mock
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get('/v1/thermostats')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_thermostats_returns_only_authorized_resources(
    thermostat: Thermostat,
    token_data_with_access_scopes: Callable,
    thermostats_service_mock: Mock,
    hvac_zones_service_mock: Mock,
    locations_service_mock: Mock,
    user_access_grants_helper_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.HVAC_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    user_access_grants_helper_mock.is_user_authorized_for_location_read.side_effect = [True, False]
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    thermostats_service_mock.filter_by.return_value = [
        thermostat,
        Thermostat(
            thermostat_id=uuid4(),
            name='Thermostat 2',
            duid='DUID2',
            modbus_address=2,
            model=ThermostatModelEnum.v1,
            node_id=uuid4(),
            hvac_zone_id=uuid4(),
            keypad_lockout=ThermostatLockoutType.UNLOCKED,
            fan_mode=ThermostatHvacFanMode.AUTO,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    app.dependency_overrides[get_thermostats_service] = lambda: thermostats_service_mock
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get('/v1/thermostats')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'thermostat_id': str(thermostat.thermostat_id),
        'name': thermostat.name,
        'duid': thermostat.duid,
        'modbus_address': thermostat.modbus_address,
        'model': str(thermostat.model),
        'node_id': str(thermostat.node_id),
        'hvac_zone_id': str(thermostat.hvac_zone_id),
        'keypad_lockout': str(thermostat.keypad_lockout),
        'fan_mode': str(thermostat.fan_mode),
        'created_at': thermostat.created_at.isoformat(),
        'updated_at': thermostat.updated_at.isoformat()
    }]


def test_list_thermostats_parses_query_parameters(
    admin_all_access_token_data: AccessTokenData,
    thermostat: Thermostat,
    thermostats_service_mock: Mock,
    hvac_zones_service_mock: Mock,
    locations_service_mock: Mock,
    user_access_grants_helper_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    user_access_grants_helper_mock.is_user_authorized_for_location_read.return_value = True
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    thermostats_service_mock.filter_by.return_value = [thermostat, ]
    app.dependency_overrides[get_thermostats_service] = lambda: thermostats_service_mock
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    params = {
        'name': 'test_name',
        'duid': '1234asdf',
        'model': 'test_model',
        'modbus_address': '1',
        'hvac_zone_id': uuid4()
    }

    response = test_client.get(
        '/v1/thermostats',
        params=params
    )

    assert response.status_code == status.HTTP_200_OK
    assert thermostats_service_mock.filter_by.call_args.kwargs == params
