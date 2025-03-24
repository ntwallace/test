from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_clamps_service, get_circuits_service, get_electric_panels_service, get_access_token_data
from app.v1.electricity_monitoring.schemas.clamp import Clamp
from app.v1.electricity_monitoring.schemas.circuit import Circuit
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanel
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_delete_clamp_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.delete(f'/v1/clamps/{uuid4()}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.ELECTRICITY_MONITORING_WRITE], status.HTTP_204_NO_CONTENT),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ELECTRICITY_MONITORING_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ELECTRICITY_MONITORING_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_delete_clamp_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    clamps_service_mock: Mock,
    circuits_service_mock: Mock,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel,
    circuit: Circuit,
    clamp: Clamp
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    clamps_service_mock.get_clamp_by_id.return_value = clamp
    clamps_service_mock.delete_clamp.return_value = None
    app.dependency_overrides[get_clamps_service] = lambda: clamps_service_mock

    circuits_service_mock.get_circuit_by_id.return_value = circuit
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock

    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.delete(f'/v1/clamps/{clamp.clamp_id}')
    
    assert response.status_code == response_code


def test_delete_clamp_success_response(
    admin_all_access_token_data: AccessTokenData,
    clamps_service_mock: Mock,
    circuits_service_mock: Mock,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel,
    circuit: Circuit,
    clamp: Clamp
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    clamps_service_mock.get_clamp_by_id.return_value = clamp
    clamps_service_mock.delete_clamp.return_value = None
    app.dependency_overrides[get_clamps_service] = lambda: clamps_service_mock

    circuits_service_mock.get_circuit_by_id.return_value = circuit
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock

    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.delete(f'/v1/clamps/{clamp.clamp_id}')

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_clamp_response_when_clamp_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    clamps_service_mock: Mock,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    clamps_service_mock.get_clamp_by_id.return_value = None
    app.dependency_overrides[get_clamps_service] = lambda: clamps_service_mock

    response = test_client.delete(f'/v1/clamps/{uuid4()}')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_clamp_when_circuit_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    clamps_service_mock: Mock,
    circuits_service_mock: Mock,
    clamp: Clamp
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    clamps_service_mock.get_clamp_by_id.return_value = clamp
    app.dependency_overrides[get_clamps_service] = lambda: clamps_service_mock

    circuits_service_mock.get_circuit_by_id.return_value = None
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock

    response = test_client.delete(f'/v1/clamps/{clamp.clamp_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_clamp_when_electric_panel_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    clamps_service_mock: Mock,
    circuits_service_mock: Mock,
    electric_panels_service_mock: Mock,
    clamp: Clamp,
    circuit: Circuit
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    clamps_service_mock.get_clamp_by_id.return_value = clamp
    app.dependency_overrides[get_clamps_service] = lambda: clamps_service_mock

    circuits_service_mock.get_circuit_by_id.return_value = circuit
    app.dependency_overrides[get_circuits_service] = lambda: circuits_service_mock

    electric_panels_service_mock.get_electric_panel_by_id.return_value = None
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.delete(f'/v1/clamp/{clamp.clamp_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
