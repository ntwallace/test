from typing import Callable, List, Optional
from unittest.mock import Mock

import pytest

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.v1.dependencies import get_gateways_service, get_access_token_data
from app.v1.locations.schemas.location import Location
from app.v1.mesh_network.schemas.gateway import Gateway
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_create_gateway_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post('/v1/gateways')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.MESH_NETWORKS_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.MESH_NETWORKS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.MESH_NETWORKS_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_gateway_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    gateways_service_mock: Mock,
    gateway: Gateway,
    location: Location
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    gateways_service_mock.create_gateway.return_value = gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.post(
        '/v1/gateways',
        json={
            'name': 'Test Gateway',
            'duid': 'test_duid',
            'location_id': str(location.location_id)
        }
    )

    assert response.status_code == response_code


def test_create_gateway_success_response(
    admin_all_access_token_data: AccessTokenData,
    gateways_service_mock: Mock,
    gateway: Gateway,
    location: Location
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    gateways_service_mock.create_gateway.return_value = gateway
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.post(
        '/v1/gateways',
        json={
            'name': 'Test Gateway',
            'duid': 'test_duid',
            'location_id': str(location.location_id)
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'gateway_id': str(gateway.gateway_id),
        'name': 'Test Gateway',
        'duid': 'test_duid',
        'location_id': str(location.location_id),
        'created_at': gateway.created_at.isoformat(),
        'updated_at': gateway.updated_at.isoformat()
    }


def test_create_gateway_when_gateway_exists(
    admin_all_access_token_data: AccessTokenData,
    gateways_service_mock: Mock,
    location: Location
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    gateways_service_mock.create_gateway.side_effect = IntegrityError('mock', 'mock', 'mock')
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.post(
        '/v1/gateways',
        json={
            'name': 'Test Gateway',
            'duid': 'test_duid',
            'location_id': str(location.location_id)
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
