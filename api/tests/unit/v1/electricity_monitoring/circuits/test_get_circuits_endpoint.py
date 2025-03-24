from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_circuits_service, get_electric_panels_service, get_access_token_data
from app.v1.electricity_monitoring.schemas.circuit import Circuit, CircuitTypeEnum
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanel
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_get_circuits_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/circuits?electric_panel_id={uuid4()}')
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
def test_get_circuits_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    circuits_service_mock: Mock,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel,
    circuits: List[Circuit]
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    circuits_service_mock.get_circuits_by_electric_panel.return_value = circuits
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock

    response = test_client.get(f'/v1/circuits?electric_panel_id={electric_panel.electric_panel_id}')
    
    assert response.status_code == response_code


def test_get_circuits_success_response(
    admin_all_access_token_data: AccessTokenData,
    circuits_service_mock: Mock,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel,
    circuits: List[Circuit]
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    circuits_service_mock.filter_by.return_value = circuits
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock

    response = test_client.get(f'/v1/circuits?electric_panel_id={electric_panel.electric_panel_id}')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'circuit_id': str(circuit.circuit_id),
            'name': circuit.name,
            'electric_panel_id': str(circuit.electric_panel_id),
            'type': circuit.type.value,
            'created_at': circuit.created_at.isoformat(),
            'updated_at': circuit.updated_at.isoformat()
        }
        for circuit in circuits
    ]


def test_get_circuits_response_when_circuits_dont_exist(
    admin_all_access_token_data: AccessTokenData,
    circuits_service_mock: Mock,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    circuits_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock

    response = test_client.get(f'/v1/circuits?electric_panel_id={electric_panel.electric_panel_id}')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_circuits_when_electric_panel_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    electric_panels_service_mock: Mock,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    electric_panels_service_mock.filter_by.return_value = None
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.get(f'/v1/circuits?electric_panel_id={uuid4()}')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_circuits_when_location_is_unauthorized(
    no_access_token_data: AccessTokenData,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel
):
    electric_panel.location_id = uuid4()
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data
    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.get(f'/v1/circuits?electric_panel_id={electric_panel.electric_panel_id}')
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_circuits_uses_filters(
    admin_all_access_token_data: AccessTokenData,
    circuit: Circuit,
    circuits_service_mock: Mock,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    circuits_service_mock.filter_by.return_value = [circuit, ]
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock

    response = test_client.get(f'/v1/circuits?name=test_name&type=main&electric_panel_id={circuit.electric_panel_id}')
    
    circuits_service_mock.filter_by.assert_called_once_with(name='test_name', type=CircuitTypeEnum.main, electric_panel_id=circuit.electric_panel_id)
    assert response.status_code == status.HTTP_200_OK
