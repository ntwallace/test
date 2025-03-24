from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_gateways_service, get_access_token_data
from app.v1.mesh_network.schemas.gateway import Gateway
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_delete_gateway_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.delete(f'/v1/gateways/{uuid4()}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.MESH_NETWORKS_WRITE], status.HTTP_204_NO_CONTENT),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.MESH_NETWORKS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.MESH_NETWORKS_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_delete_gateway_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    gateways_service_mock: Mock,
    gateway: Gateway,
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    gateways_service_mock.delete_gateway.return_value = None
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.delete(f'/v1/gateways/{gateway.gateway_id}')

    assert response.status_code == response_code


def test_delete_gateway_success_response(
    admin_all_access_token_data: AccessTokenData,
    gateways_service_mock: Mock,
    gateway: Gateway,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    gateways_service_mock.delete_gateway.return_value = None
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.delete(f'/v1/gateways/{gateway.gateway_id}')

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_gateway_when_gateway_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    gateways_service_mock: Mock,
    gateway: Gateway,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    gateways_service_mock.get_gateway_by_gateway_id.return_value = None
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.delete(f'/v1/gateways/{gateway.gateway_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
