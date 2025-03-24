from typing import Callable, List
from unittest.mock import Mock
from fastapi import status
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.v1.dependencies import get_access_token_data, get_circuits_service, get_electric_panels_service, get_locations_service
from app.v1.electricity_monitoring.schemas.circuit import Circuit
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_create_circuit_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post('/v1/circuits')
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
def test_create_circuit_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    circuits_service_mock: Mock,
    electric_panels_service_mock: Mock,
    locations_service_mock: Mock,
    circuit: Circuit
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    circuits_service_mock.create_circuit.return_value = circuit
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.post('/v1/circuits', json={
        "name": "Test Circuit 1",
        "type": "main",
        "electric_panel_id": str(circuit.electric_panel_id),
        "circuit_id": str(circuit.circuit_id)
    })

    assert response.status_code == response_code


def test_create_circuit_success_response(
    admin_all_access_token_data: AccessTokenData,
    circuit: Circuit,
    circuits_service_mock: Mock,
    electric_panels_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    circuits_service_mock.create_circuit.return_value = circuit
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.post('/v1/circuits', json={
        "name": "Test Circuit 1",
        "type": "main",
        "electric_panel_id": str(circuit.electric_panel_id),
        "circuit_id": str(circuit.circuit_id)
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "circuit_id": str(circuit.circuit_id),
        "name": "Test Circuit 1",
        "type": "main",
        "electric_panel_id": str(circuit.electric_panel_id),
        "created_at": circuit.created_at.isoformat(),
        "updated_at": circuit.updated_at.isoformat()
    }


def test_create_circuit_when_circuit_already_exists(
    admin_all_access_token_data: AccessTokenData,
    circuit: Circuit,
    circuits_service_mock: Mock,
    electric_panels_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    circuits_service_mock.create_circuit.side_effect = ValueError('Circuit already exists')
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.post('/v1/circuits', json={
        "name": "Test Circuit 1",
        "type": "main",
        "electric_panel_id": str(circuit.electric_panel_id),
        "circuit_id": str(circuit.circuit_id)
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
