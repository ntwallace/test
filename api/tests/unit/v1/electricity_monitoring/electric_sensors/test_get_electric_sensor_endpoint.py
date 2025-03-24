from datetime import datetime
from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import (
    get_electric_sensors_service,
    get_electric_panels_service,
    get_access_token_data,
    get_gateways_service
)
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanel
from app.v1.electricity_monitoring.schemas.electric_sensor import ElectricSensor
from app.v1.mesh_network.schemas.gateway import Gateway
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_get_electric_sensor_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/electric-sensors/{uuid4()}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ELECTRICITY_MONITORING_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ELECTRICITY_MONITORING_READ], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_get_electricity_sensor_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    electric_sensors_service_mock: Mock,
    electric_panels_service_mock: Mock,
    gateways_service_mock: Mock,
    electric_panel: ElectricPanel,
    gateway: Gateway,
    electric_sensor: ElectricSensor
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    electric_sensors_service_mock.get_electric_sensor_by_id.return_value = electric_sensor
    app.dependency_overrides[get_electric_sensors_service] = lambda: electric_sensors_service_mock

    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.get(f'/v1/electric-sensors/{electric_sensor.electric_sensor_id}')
    
    assert response.status_code == response_code


def test_get_electric_sensor_success_response(
    admin_all_access_token_data: AccessTokenData,
    electric_sensors_service_mock: Mock,
    electric_panels_service_mock: Mock,
    gateways_service_mock: Mock,
    electric_panel: ElectricPanel,
    gateway: Gateway,
    electric_sensor: ElectricSensor
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    electric_sensors_service_mock.get_electric_sensor_by_id.return_value = electric_sensor
    app.dependency_overrides[get_electric_sensors_service] = lambda: electric_sensors_service_mock

    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.get(f'/v1/electric-sensors/{electric_sensor.electric_sensor_id}')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'name': electric_sensor.name,
        'duid': 'aaaaaaaa',
        'port_count': electric_sensor.port_count,
        'electric_panel_id': str(electric_sensor.electric_panel_id),
        'gateway_id': str(electric_sensor.gateway_id),
        'a_breaker_num': electric_sensor.a_breaker_num,
        'b_breaker_num': electric_sensor.b_breaker_num,
        'c_breaker_num': electric_sensor.c_breaker_num,
        'electric_sensor_id': str(electric_sensor.electric_sensor_id),
        'created_at': electric_sensor.created_at.isoformat(),
        'updated_at': electric_sensor.updated_at.isoformat()
    }


def test_get_electric_sensor_without_panel_success_response(
    admin_all_access_token_data: AccessTokenData,
    electric_sensors_service_mock: Mock,
    gateways_service_mock: Mock,
    gateway: Gateway,
    electric_sensor: ElectricSensor
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    electric_sensor.electric_panel_id = None
    electric_sensors_service_mock.get_electric_sensor_by_id.return_value = electric_sensor
    app.dependency_overrides[get_electric_sensors_service] = lambda: electric_sensors_service_mock

    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.get(f'/v1/electric-sensors/{electric_sensor.electric_sensor_id}')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'name': electric_sensor.name,
        'duid': 'aaaaaaaa',
        'port_count': electric_sensor.port_count,
        'electric_panel_id': None,
        'gateway_id': str(electric_sensor.gateway_id),
        'a_breaker_num': electric_sensor.a_breaker_num,
        'b_breaker_num': electric_sensor.b_breaker_num,
        'c_breaker_num': electric_sensor.c_breaker_num,
        'electric_sensor_id': str(electric_sensor.electric_sensor_id),
        'created_at': electric_sensor.created_at.isoformat(),
        'updated_at': electric_sensor.updated_at.isoformat()
    }


def test_get_electric_sensor_when_electric_sensor_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    electric_sensors_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    electric_sensors_service_mock.get_electric_sensor_by_id.return_value = None
    app.dependency_overrides[get_electric_sensors_service] = lambda: electric_sensors_service_mock

    response = test_client.get(f'/v1/electric-sensors/{uuid4()}')
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_electric_sensor_when_location_is_unauthorized(
    no_access_token_data: AccessTokenData,
    electric_sensors_service_mock: Mock,
    electric_panels_service_mock: Mock,
    gateways_service_mock: Mock,
    electric_panel: ElectricPanel,
    gateway: Gateway,
    electric_sensor: ElectricSensor
):
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data

    electric_sensors_service_mock.get_electric_sensor_by_id.return_value = electric_sensor
    app.dependency_overrides[get_electric_sensors_service] = lambda: electric_sensors_service_mock

    electric_panel.location_id = uuid4()
    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    gateway.location_id = uuid4()
    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.get(f'/v1/electric-sensors/{electric_sensor.electric_sensor_id}')
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_electric_sensor_when_electric_panel_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    electric_sensors_service_mock: Mock,
    gateways_service_mock: Mock,
    gateway: Gateway
):
    electric_sensor = ElectricSensor(
        electric_sensor_id=uuid4(),
        name='Test Electric Sensor',
        duid='aaaaaaaa',
        port_count=3,
        electric_panel_id=None,
        gateway_id=gateway.gateway_id,
        a_breaker_num=1,
        b_breaker_num=2,
        c_breaker_num=3,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    electric_sensors_service_mock.get_electric_sensor_by_id.return_value = electric_sensor
    app.dependency_overrides[get_electric_sensors_service] = lambda: electric_sensors_service_mock

    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    response = test_client.get(f'/v1/electric-sensors/{electric_sensor.electric_sensor_id}')    

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'name': electric_sensor.name,
        'duid': 'aaaaaaaa',
        'port_count': electric_sensor.port_count,
        'electric_panel_id': None,
        'gateway_id': str(electric_sensor.gateway_id),
        'a_breaker_num': electric_sensor.a_breaker_num,
        'b_breaker_num': electric_sensor.b_breaker_num,
        'c_breaker_num': electric_sensor.c_breaker_num,
        'electric_sensor_id': str(electric_sensor.electric_sensor_id),
        'created_at': electric_sensor.created_at.isoformat(),
        'updated_at': electric_sensor.updated_at.isoformat()
    }
