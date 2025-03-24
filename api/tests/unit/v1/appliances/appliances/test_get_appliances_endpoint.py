from typing import Callable, List
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


def test_get_appliances_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/appliances?location_id={uuid4()}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.APPLIANCES_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.APPLIANCES_READ], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_get_appliances_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    appliances_service_mock: Mock,
    appliance: Appliance,
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    appliances_service_mock.get_appliances_by_location.return_value = [appliance,]
    app.dependency_overrides[get_appliances_service] = lambda: appliances_service_mock

    response = test_client.get(f'/v1/appliances?location_id={appliance.location_id}')

    assert response.status_code == response_code


def test_get_appliances_success_response(
    admin_all_access_token_data: AccessTokenData,
    appliances_service_mock: Mock,
    appliance: Appliance,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    appliances_service_mock.get_appliances_by_location.return_value = [appliance,]
    app.dependency_overrides[get_appliances_service] = lambda: appliances_service_mock

    response = test_client.get(f'/v1/appliances?location_id={appliance.location_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'appliance_id': str(appliance.appliance_id),
        'name': appliance.name,
        'appliance_super_type': appliance.appliance_super_type,
        'appliance_type_id': str(appliance.appliance_type_id),
        'location_id': str(appliance.location_id),
        'circuit_id': str(appliance.circuit_id),
        'temperature_sensor_place_id': str(appliance.temperature_sensor_place_id),
        'serial': appliance.serial,
        'created_at': appliance.created_at.isoformat(),
        'updated_at': appliance.updated_at.isoformat()
    }]


def test_get_appliances_when_appliances_dont_exist(
    admin_all_access_token_data: AccessTokenData,
    appliances_service_mock: Mock,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    appliances_service_mock.get_appliances_by_location.return_value = []
    app.dependency_overrides[get_appliances_service] = lambda: appliances_service_mock

    response = test_client.get(f'/v1/appliances?location_id={uuid4()}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_appliances_when_location_not_authorized(
    no_access_token_data: Callable
):
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data

    response = test_client.get(f'/v1/appliances?location_id={uuid4()}')

    assert response.status_code == status.HTTP_403_FORBIDDEN
