from typing import Callable, List
from unittest.mock import Mock

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import get_api_key_access_scopes_helper, get_api_key_data, get_thermostats_service, get_hvac_zones_service, get_nodes_service, get_gateways_service, get_access_token_data
from app.v1.hvac.schemas.thermostat import Thermostat
from app.v1.hvac.schemas.hvac_zone import HvacZone
from app.v1.mesh_network.schemas.node import Node
from app.v1.mesh_network.schemas.gateway import Gateway
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_create_thermostat_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post('/v1/thermostats')
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
def test_create_thermostat_access_scopes(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    thermostats_service_mock: Mock,
    thermostat: Thermostat,
    hvac_zones_service_mock: Mock,
    hvac_zone: HvacZone,
    nodes_service_mock: Mock,
    node: Node,
    gateways_service_mock: Mock,
    gateway: Gateway
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    thermostats_service_mock.create_thermostat.return_value =  thermostat
    app.dependency_overrides[get_thermostats_service] = lambda:  thermostats_service_mock

    hvac_zones_service_mock.get_hvac_zone_by_id.return_value = hvac_zone
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock

    nodes_service_mock.get_node_by_node_id.return_value = node
    app.dependency_overrides[get_nodes_service] = lambda: nodes_service_mock

    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.post('/v1/thermostats', json={
        'name': 'Test Thermostat',
        'duid': str(thermostat.duid),
        'modbus_address': thermostat.modbus_address,
        'model': thermostat.model.value,
        'node_id': str(thermostat.node_id),
        'hvac_zone_id': str(thermostat.hvac_zone_id)
    })

    assert response.status_code == response_code


def test_create_thermostat_success_response_when_jwt_auth(
    admin_all_access_token_data: AccessTokenData,
    thermostats_service_mock: Mock,
    thermostat: Thermostat,
    hvac_zones_service_mock: Mock,
    hvac_zone: HvacZone,
    nodes_service_mock: Mock,
    node: Node,
    gateways_service_mock: Mock,
    gateway: Gateway
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    thermostats_service_mock.create_thermostat.return_value = thermostat
    app.dependency_overrides[get_thermostats_service] = lambda: thermostats_service_mock

    hvac_zones_service_mock.get_hvac_zone_by_id.return_value = hvac_zone
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock

    nodes_service_mock.get_node_by_node_id.return_value = node
    app.dependency_overrides[get_nodes_service] = lambda: nodes_service_mock

    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.post('/v1/thermostats', json={
        'name': str(thermostat.name),
        'duid': str(thermostat.duid),
        'modbus_address': thermostat.modbus_address,
        'model': thermostat.model.value,
        'node_id': str(thermostat.node_id),
        'hvac_zone_id': str(thermostat.hvac_zone_id)
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'name': str(thermostat.name),
        'thermostat_id': str(thermostat.thermostat_id),
        'duid': str(thermostat.duid),
        'modbus_address': thermostat.modbus_address,
        'model': thermostat.model.value,
        'node_id': str(thermostat.node_id),
        'hvac_zone_id': str(thermostat.hvac_zone_id),
        'fan_mode': thermostat.fan_mode.value,
        'keypad_lockout': thermostat.keypad_lockout.value,
        'created_at': thermostat.created_at.isoformat(),
        'updated_at': thermostat.updated_at.isoformat()
    }


def test_create_thermostat_success_response_when_api_key_auth(
    api_key: APIKey,
    api_key_access_scopes_helper_mock: Mock,
    thermostats_service_mock: Mock,
    thermostat: Thermostat,
    hvac_zones_service_mock: Mock,
    nodes_service_mock: Mock,
    gateways_service_mock: Mock,
):
    app.dependency_overrides[get_api_key_data] = lambda: api_key

    api_key_access_scopes_helper_mock.get_all_access_scopes_for_api_key.return_value = [AccessScope.HVAC_WRITE, AccessScope.ADMIN]
    app.dependency_overrides[get_api_key_access_scopes_helper] = lambda: api_key_access_scopes_helper_mock

    app.dependency_overrides[get_thermostats_service] = lambda: thermostats_service_mock
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock
    app.dependency_overrides[get_nodes_service] = lambda: nodes_service_mock
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.post('/v1/thermostats', json={
        'name': str(thermostat.name),
        'duid': str(thermostat.duid),
        'modbus_address': thermostat.modbus_address,
        'model': thermostat.model.value,
        'node_id': str(thermostat.node_id),
        'hvac_zone_id': str(thermostat.hvac_zone_id)
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'name': str(thermostat.name),
        'thermostat_id': str(thermostat.thermostat_id),
        'duid': str(thermostat.duid),
        'modbus_address': thermostat.modbus_address,
        'model': thermostat.model.value,
        'node_id': str(thermostat.node_id),
        'hvac_zone_id': str(thermostat.hvac_zone_id),
        'fan_mode': thermostat.fan_mode.value,
        'keypad_lockout': thermostat.keypad_lockout.value,
        'created_at': thermostat.created_at.isoformat(),
        'updated_at': thermostat.updated_at.isoformat()
    }


def test_create_thermostat_when_exists(
    admin_all_access_token_data: AccessTokenData,
    thermostats_service_mock: Mock,
    thermostat: Thermostat,
    hvac_zones_service_mock: Mock,
    hvac_zone: HvacZone,
    nodes_service_mock: Mock,
    node: Node,
    gateways_service_mock: Mock,
    gateway: Gateway
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    thermostats_service_mock.create_thermostat.side_effect = ValueError
    app.dependency_overrides[get_thermostats_service] = lambda:  thermostats_service_mock

    hvac_zones_service_mock.get_hvac_zone_by_id.return_value = hvac_zone
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock

    nodes_service_mock.get_node_by_node_id.return_value = node
    app.dependency_overrides[get_nodes_service] = lambda: nodes_service_mock

    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.post('/v1/thermostats', json={
        'name': 'Test Thermostat',
        'duid': str(thermostat.duid),
        'modbus_address': thermostat.modbus_address,
        'model': thermostat.model.value,
        'node_id': str(thermostat.node_id),
        'hvac_zone_id': str(thermostat.hvac_zone_id)
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
