from typing import Callable, List, Optional
from unittest.mock import Mock

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_appliance_types_service, get_access_token_data
from app.v1.appliances.schemas.appliance_type import ApplianceType
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_create_appliance_types_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post('/v1/appliance-types')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.APPLIANCES_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.APPLIANCES_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.APPLIANCES_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_appliance_types_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    appliance_types_service_mock: Mock,
    appliance_type: ApplianceType
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    appliance_types_service_mock.get_appliance_by_make_model_type_subtype_year.return_value = None
    appliance_types_service_mock.create_appliance_type.return_value = appliance_type
    app.dependency_overrides[get_appliance_types_service] = lambda: appliance_types_service_mock

    response = test_client.post('/v1/appliance-types', json={
        'make': 'make',
        'model': 'model',
        'type': 'type',
        'subtype': 'subtype',
        'year_manufactured': 2021
    })

    assert response.status_code == response_code


def test_create_appliance_types_success_response(
    admin_all_access_token_data: AccessTokenData,
    appliance_types_service_mock: Mock,
    appliance_type: ApplianceType
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    appliance_types_service_mock.get_appliance_by_make_model_type_subtype_year.return_value = None
    appliance_types_service_mock.create_appliance_type.return_value = appliance_type
    app.dependency_overrides[get_appliance_types_service] = lambda: appliance_types_service_mock

    response = test_client.post('/v1/appliance-types', json={
        'make': 'make',
        'model': 'model',
        'type': 'type',
        'subtype': 'subtype',
        'year_manufactured': 2021
    })

    assert response.status_code == status.HTTP_201_CREATED
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


def test_create_appliance_types_when_appliance_type_already_exists(
    admin_all_access_token_data: AccessTokenData,
    appliance_types_service_mock: Mock,
    appliance_type: ApplianceType
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    appliance_types_service_mock.get_appliance_by_make_model_type_subtype_year.return_value = appliance_type
    app.dependency_overrides[get_appliance_types_service] = lambda: appliance_types_service_mock

    response = test_client.post('/v1/appliance-types', json={
        'make': 'make',
        'model': 'model',
        'type': 'type',
        'subtype': 'subtype',
        'year_manufactured': 2021
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
