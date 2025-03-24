from typing import Callable, List
from unittest.mock import Mock
from uuid import UUID, uuid4
from fastapi import status
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.v1.dependencies import get_access_token_data, get_gateways_service, get_nodes_service, get_user_access_grants_helper
from app.v1.mesh_network.schemas.node import Node
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_get_node_is_unauthorized_without_token(node: Node):
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/nodes/{node.node_id}')
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
def test_get_node_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    nodes_service_mock: Mock,
    node: Node
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    nodes_service_mock.get_node_by_node_id.return_value = node
    app.dependency_overrides[get_nodes_service] = lambda: nodes_service_mock

    response = test_client.get(f'/v1/nodes/{node.node_id}')

    assert response.status_code == response_code


def test_get_node_success_response(
    admin_all_access_token_data: AccessTokenData,
    nodes_service_mock: Mock,
    node: Node
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    nodes_service_mock.get_node_by_node_id.return_value = node
    app.dependency_overrides[get_nodes_service] = lambda: nodes_service_mock
    
    response = test_client.get(f'/v1/nodes/{node.node_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'node_id': str(node.node_id),
        'name': node.name,
        'duid': node.duid,
        'type': node.type,
        'gateway_id': str(node.gateway_id),
        'created_at': node.created_at.isoformat(),
        'updated_at': node.updated_at.isoformat()
    }


def test_get_node_when_node_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    nodes_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    nodes_service_mock.get_node_by_node_id.return_value = None
    app.dependency_overrides[get_nodes_service] = lambda: nodes_service_mock
    
    response = test_client.get(f'/v1/nodes/{uuid4()}')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_node_when_user_isnt_authorized_for_access(
    token_data_with_access_scopes: Callable,
    nodes_service_mock: Mock,
    user_access_grants_helper_mock: Mock,
    node: Node
):
    app.dependency_overrides[get_access_token_data] = lambda: token_data_with_access_scopes([AccessScope.MESH_NETWORKS_READ])

    user_access_grants_helper_mock.is_user_authorized_for_location_read.return_value = False
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    nodes_service_mock.get_node_by_node_id.return_value = node
    app.dependency_overrides[get_nodes_service] = lambda: nodes_service_mock
    
    response = test_client.get(f'/v1/nodes/{node.node_id}')

    assert response.status_code == status.HTTP_403_FORBIDDEN
