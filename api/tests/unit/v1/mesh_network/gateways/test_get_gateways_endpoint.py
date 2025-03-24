from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_gateways_service, get_access_token_data
from app.v1.locations.schemas.location import Location
from app.v1.mesh_network.schemas.gateway import Gateway
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_get_gateways_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get('/v1/gateways')
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
def test_get_gateways_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    gateways_service_mock: Mock,
    gateway: Gateway,
    location: Location
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    gateways_service_mock.filter_by.return_value = [gateway,]
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.get(f'/v1/gateways?location_id={location.location_id}')

    assert response.status_code == response_code


def test_get_gateways_success_response(
    admin_all_access_token_data: AccessTokenData,
    gateways_service_mock: Mock,
    gateway: Gateway,
    location: Location
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    gateways_service_mock.filter_by.return_value = [gateway,]
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.get(f'/v1/gateways?location_id={location.location_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'gateway_id': str(gateway.gateway_id),
        'name': gateway.name,
        'duid': gateway.duid,
        'location_id': str(gateway.location_id),
        'created_at': gateway.created_at.isoformat(),
        'updated_at': gateway.updated_at.isoformat()
    }]


def test_get_gateways_returns_empty_list_when_no_gateways(
    admin_all_access_token_data: AccessTokenData,
    gateways_service_mock: Mock,
    location: Location
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    gateways_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.get(f'/v1/gateways?location_id={location.location_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_gateways_when_accessing_unauthorized_location(
    no_access_token_data: AccessTokenData
):
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data

    response = test_client.get(f'/v1/gateways?location_id={uuid4()}')

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_gateways_with_filters(
    admin_all_access_token_data: AccessTokenData,
    gateways_service_mock: Mock,
    gateway: Gateway,
    location: Location
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    gateways_service_mock.filter_by.return_value = [gateway,]
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock

    response = test_client.get(f'/v1/gateways?location_id={location.location_id}&name=Test&duid=asdf1234')

    assert gateways_service_mock.filter_by.call_args.kwargs == {
        'location_id': location.location_id,
        'name': 'Test',
        'duid': 'asdf1234'
    }

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'gateway_id': str(gateway.gateway_id),
        'name': gateway.name,
        'duid': gateway.duid,
        'location_id': str(gateway.location_id),
        'created_at': gateway.created_at.isoformat(),
        'updated_at': gateway.updated_at.isoformat()
    }]
