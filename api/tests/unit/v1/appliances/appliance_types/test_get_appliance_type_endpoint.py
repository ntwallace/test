from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_appliance_types_service, get_access_token_data
from app.v1.appliances.schemas.appliance_type import ApplianceType
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_get_appliance_type_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/appliance-types/{uuid4()}')
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
def test_get_appliance_type_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    appliance_types_service_mock: Mock,
    appliance_type: ApplianceType
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    appliance_types_service_mock.get_appliance_type_by_id.return_value = appliance_type
    app.dependency_overrides[get_appliance_types_service] = lambda: appliance_types_service_mock

    response = test_client.get(f'/v1/appliance-types/{appliance_type.appliance_type_id}')

    assert response.status_code == response_code


def test_get_appliance_type_success_response(
    admin_all_access_token_data: AccessTokenData,
    appliance_types_service_mock: Mock,
    appliance_type: ApplianceType
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    appliance_types_service_mock.get_appliance_type_by_id.return_value = appliance_type
    app.dependency_overrides[get_appliance_types_service] = lambda: appliance_types_service_mock

    response = test_client.get(f'/v1/appliance-types/{appliance_type.appliance_type_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'appliance_type_id': str(appliance_type.appliance_type_id),
        'make': appliance_type.make,
        'model': appliance_type.model,
        'type': appliance_type.type,
        'subtype': appliance_type.subtype,
        'year_manufactured': appliance_type.year_manufactured,
        'created_at': appliance_type.created_at.isoformat(),
        'updated_at': appliance_type.updated_at.isoformat()
    }


def test_get_appliance_type_when_appliance_type_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    appliance_types_service_mock: Mock,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    appliance_types_service_mock.get_appliance_type_by_id.return_value = None
    app.dependency_overrides[get_appliance_types_service] = lambda: appliance_types_service_mock

    response = test_client.get(f'/v1/appliance-types/{uuid4()}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
