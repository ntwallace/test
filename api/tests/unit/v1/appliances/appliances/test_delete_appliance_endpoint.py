from typing import Callable, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.appliances.schemas.appliance import Appliance
from app.v1.dependencies import get_appliances_service, get_access_token_data
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_delete_appliance_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.delete(f'/v1/appliances/{uuid4()}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.APPLIANCES_WRITE], status.HTTP_204_NO_CONTENT),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.APPLIANCES_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.APPLIANCES_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_delete_appliance_access_scope_responses(
    access_scopes: Optional[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    appliances_service_mock: Mock,
    appliance: Appliance,
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    appliances_service_mock.get_appliance_by_id.return_value = appliance
    appliances_service_mock.delete_appliance.return_value = None
    app.dependency_overrides[get_appliances_service] = lambda: appliances_service_mock

    response = test_client.delete(f'/v1/appliances/{appliance.appliance_id}')

    assert response.status_code == response_code


def test_delete_appliance_success_response(
    admin_all_access_token_data: AccessTokenData,
    appliances_service_mock: Mock,
    appliance: Appliance,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    appliances_service_mock.get_appliance_by_id.return_value = appliance
    appliances_service_mock.delete_appliance.return_value = None
    app.dependency_overrides[get_appliances_service] = lambda: appliances_service_mock

    response = test_client.delete(f'/v1/appliances/{appliance.appliance_id}')

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_delete_appliance_when_appliance_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    appliances_service_mock: Mock,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    appliances_service_mock.get_appliance_by_id.return_value = None
    app.dependency_overrides[get_appliances_service] = lambda: appliances_service_mock

    response = test_client.delete(f'/v1/appliances/{uuid4()}')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_appliance_when_location_not_authorized(
    no_access_token_data: Callable,
    appliances_service_mock: Mock,
    appliance: Appliance
):
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data

    appliance.location_id = uuid4()
    appliances_service_mock.get_appliance_by_id.return_value = appliance
    app.dependency_overrides[get_appliances_service] = lambda: appliances_service_mock

    response = test_client.delete(f'/v1/appliances/{appliance.appliance_id}')

    assert response.status_code == status.HTTP_403_FORBIDDEN
