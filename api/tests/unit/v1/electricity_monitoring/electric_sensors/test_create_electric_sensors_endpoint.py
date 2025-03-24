from typing import Callable, List
from unittest.mock import Mock
from fastapi import status
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.v1.dependencies import get_access_token_data, get_electric_sensors_service, get_electric_panels_service, get_locations_service, get_gateways_service
from app.v1.electricity_monitoring.schemas.electric_sensor import ElectricSensor
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_create_electric_sensor_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post('/v1/electric-sensors')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.ELECTRICITY_MONITORING_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ELECTRICITY_MONITORING_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ELECTRICITY_MONITORING_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_electric_sensor_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    electric_sensors_service_mock: Mock,
    electric_panels_service_mock: Mock,
    gateways_service_mock: Mock,
    locations_service_mock: Mock,
    electric_sensor: ElectricSensor
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    electric_sensors_service_mock.create_electric_sensor.return_value = electric_sensor
    app.dependency_overrides[get_electric_sensors_service] = lambda: electric_sensors_service_mock
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.post('/v1/electric-sensors', json={
        'name': 'Test Electric Sensor 1',
        'duid': 'aaaaaaaa',
        'port_count': 3,
        'electric_panel_id': str(electric_sensor.electric_panel_id),
        'gateway_id': str(electric_sensor.gateway_id),
        'a_breaker_num': 1,
        'b_breaker_num': 2,
        'c_breaker_num': 3
    })

    assert response.status_code == response_code


def test_create_electric_sensor_success_response(
    admin_all_access_token_data: AccessTokenData,
    electric_sensor: ElectricSensor,
    electric_sensors_service_mock: Mock,
    electric_panels_service_mock: Mock,
    gateways_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    electric_sensors_service_mock.create_electric_sensor.return_value = electric_sensor
    app.dependency_overrides[get_electric_sensors_service] = lambda: electric_sensors_service_mock
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.post('/v1/electric-sensors', json={
        'name': 'Test Electric Sensor 1',
        'duid': 'aaaaaaaa',
        'port_count': 3,
        'electric_panel_id': str(electric_sensor.electric_panel_id),
        'gateway_id': str(electric_sensor.gateway_id),
        'a_breaker_num': 1,
        'b_breaker_num': 2,
        'c_breaker_num': 3
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'electric_sensor_id': str(electric_sensor.electric_sensor_id),
        'name': 'Test Electric Sensor 1',
        'duid': 'aaaaaaaa',
        'port_count': 3,
        'electric_panel_id': str(electric_sensor.electric_panel_id),
        'gateway_id': str(electric_sensor.gateway_id),
        'a_breaker_num': 1,
        'b_breaker_num': 2,
        'c_breaker_num': 3,
        'created_at': electric_sensor.created_at.isoformat(),
        'updated_at': electric_sensor.updated_at.isoformat()
    }


def test_create_electric_sensor_without_panel_success_response(
    admin_all_access_token_data: AccessTokenData,
    electric_sensor: ElectricSensor,
    electric_sensors_service_mock: Mock,
    gateways_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    electric_sensor.electric_panel_id = None
    electric_sensors_service_mock.create_electric_sensor.return_value = electric_sensor
    app.dependency_overrides[get_electric_sensors_service] = lambda: electric_sensors_service_mock
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.post('/v1/electric-sensors', json={
        'name': 'Test Electric Sensor 1',
        'duid': 'aaaaaaaa',
        'port_count': 3,
        'gateway_id': str(electric_sensor.gateway_id),
        'a_breaker_num': 1,
        'b_breaker_num': 2,
        'c_breaker_num': 3
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'electric_sensor_id': str(electric_sensor.electric_sensor_id),
        'name': 'Test Electric Sensor 1',
        'duid': 'aaaaaaaa',
        'port_count': 3,
        'electric_panel_id': None,
        'gateway_id': str(electric_sensor.gateway_id),
        'a_breaker_num': 1,
        'b_breaker_num': 2,
        'c_breaker_num': 3,
        'created_at': electric_sensor.created_at.isoformat(),
        'updated_at': electric_sensor.updated_at.isoformat()
    }


def test_create_electric_sensor_with_nonexistent_panel(
    admin_all_access_token_data: AccessTokenData,
    electric_sensor: ElectricSensor,
    electric_sensors_service_mock: Mock,
    electric_panels_service_mock: Mock,
    gateways_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    electric_panels_service_mock.get_electric_panel_by_id.return_value = None
    app.dependency_overrides[get_electric_sensors_service] = lambda: electric_sensors_service_mock
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.post('/v1/electric-sensors', json={
        'name': 'Test Electric Sensor 1',
        'duid': 'aaaaaaaa',
        'port_count': 3,
        'electric_panel_id': str(electric_sensor.electric_panel_id),
        'gateway_id': str(electric_sensor.gateway_id),
        'a_breaker_num': 1,
        'b_breaker_num': 2,
        'c_breaker_num': 3
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['detail'] == 'Electric panel does not exist'


def test_create_electric_sensor_when_electric_sensor_already_exists(
    admin_all_access_token_data: AccessTokenData,
    electric_sensor: ElectricSensor,
    electric_sensors_service_mock: Mock,
    electric_panels_service_mock: Mock,
    gateways_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    electric_sensors_service_mock.create_electric_sensor.side_effect = ValueError('ElectricSensor already exists')
    app.dependency_overrides[get_electric_sensors_service] = lambda: electric_sensors_service_mock
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.post('/v1/electric-sensors', json={
        'name': 'Test Electric Sensor 1',
        'duid': 'aaaaaaaa',
        'port_count': 3,
        'electric_panel_id': str(electric_sensor.electric_panel_id),
        'gateway_id': str(electric_sensor.gateway_id),
        'a_breaker_num': 1,
        'b_breaker_num': 2,
        'c_breaker_num': 3
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
