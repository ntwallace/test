from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_circuits_service, get_electric_panels_service, get_access_token_data
from app.v1.electricity_monitoring.schemas.circuit import Circuit
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanel
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_get_circuit_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/circuits/{uuid4()}')
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
def test_get_circuit_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    circuits_service_mock: Mock,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel,
    circuit: Circuit
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    circuits_service_mock.get_circuit_by_id.return_value = circuit
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock

    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.get(f'/v1/circuits/{circuit.circuit_id}')
    
    assert response.status_code == response_code


def test_get_circuit_success_response(
    admin_all_access_token_data: AccessTokenData,
    circuits_service_mock: Mock,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel,
    circuit: Circuit
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    circuits_service_mock.get_circuit_by_id.return_value = circuit
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock

    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.get(f'/v1/circuits/{circuit.circuit_id}')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'circuit_id': str(circuit.circuit_id),
        'name': circuit.name,
        'electric_panel_id': str(circuit.electric_panel_id),
        'type': circuit.type.value,
        'created_at': circuit.created_at.isoformat(),
        'updated_at': circuit.updated_at.isoformat()
    }


def test_get_circuit_response_when_circuit_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    circuits_service_mock: Mock,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    
    circuits_service_mock.get_circuit_by_id.return_value = None
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock

    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.get(f'/v1/circuits/{uuid4()}')
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_circuit_when_electric_panel_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    circuits_service_mock: Mock,
    electric_panels_service_mock: Mock,
    circuit: Circuit
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    circuit.electric_panel_id = uuid4()
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock

    electric_panels_service_mock.get_electric_panel_by_id.return_value = None
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.get(f'/v1/circuits/{circuit.circuit_id}')
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_circuit_when_location_is_unauthorized(
    no_access_token_data: AccessTokenData,
    electric_panels_service_mock: Mock,
    circuits_service_mock: Mock,
    electric_panel: ElectricPanel,
):
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data

    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock
    
    electric_panel.location_id = uuid4()
    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.get(f'/v1/circuits/{uuid4()}')
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
