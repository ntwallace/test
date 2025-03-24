from datetime import datetime
from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_gateways_service, get_nodes_service, get_access_token_data
from app.v1.mesh_network.schemas.gateway import Gateway
from app.v1.mesh_network.schemas.node import Node
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_get_node_for_gateway_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/gateways/{uuid4()}/nodes/{uuid4()}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.MESH_NETWORKS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.MESH_NETWORKS_READ], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_get_node_for_gateway_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    gateways_service_mock: Mock,
    nodes_service_mock: Mock,
    gateway: Gateway,
    node: Node
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock
    nodes_service_mock.get_node_for_gateway_by_node_id.return_value = node
    app.dependency_overrides[get_nodes_service] = lambda: nodes_service_mock

    response = test_client.get(f'/v1/gateways/{gateway.gateway_id}/nodes/{node.node_id}')

    assert response.status_code == response_code


def test_get_node_for_gateway_success_response(
    admin_all_access_token_data: AccessTokenData,
    gateways_service_mock: Mock,
    nodes_service_mock: Mock,
    gateway: Gateway,
    node: Node
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock
    nodes_service_mock.get_node_for_gateway_by_node_id.return_value = node
    app.dependency_overrides[get_nodes_service] = lambda: nodes_service_mock

    response = test_client.get(f'/v1/gateways/{gateway.gateway_id}/nodes/{node.node_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'name': node.name,
        'duid': node.duid,
        'gateway_id': str(node.gateway_id),
        'type': node.type.value,
        'node_id': str(node.node_id),
        'created_at': node.created_at.isoformat(),
        'updated_at': node.updated_at.isoformat()
    }


def test_get_node_for_gateway_when_node_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    gateways_service_mock: Mock,
    nodes_service_mock: Mock,
    gateway: Gateway
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock
    nodes_service_mock.get_node_for_gateway_by_node_id.return_value = None
    app.dependency_overrides[get_nodes_service] = lambda: nodes_service_mock

    response = test_client.get(f'/v1/gateways/{gateway.gateway_id}/nodes/{uuid4()}')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_node_for_gateway_when_gateway_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    gateways_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    gateways_service_mock.get_gateway_by_gateway_id.return_value = None
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.get(f'/v1/gateways/{uuid4()}/nodes/{uuid4()}')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_node_for_gateway_when_location_is_unauthorized(
    no_access_token_data: AccessTokenData,
    gateways_service_mock: Mock,
):
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data
    unauthorized_gateway = Gateway(
        gateway_id=uuid4(),
        name='Unauthorized Gateway',
        duid='unauthorized_duid',
        location_id=uuid4(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    gateways_service_mock.get_gateway_by_gateway_id.return_value = unauthorized_gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.get(f'/v1/gateways/{unauthorized_gateway.gateway_id}/nodes/{uuid4()}')

    assert response.status_code == status.HTTP_403_FORBIDDEN
