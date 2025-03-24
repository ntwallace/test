from typing import Callable, List
from unittest.mock import Mock

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_organizations_service, get_access_token_data
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.organizations.schemas.organization import Organization


test_client = TestClient(app)


def test_create_organization_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post('/v1/organizations')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.ORGANIZATIONS_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ORGANIZATIONS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ORGANIZATIONS_READ], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ORGANIZATION_USERS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ORGANIZATION_USERS_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_organization_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    organizations_service_mock: Mock
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    
    organizations_service_mock.get_organization_by_name.return_value = None
    app.dependency_overrides[get_organizations_service] = lambda: organizations_service_mock

    response = test_client.post(
        '/v1/organizations', 
        json={
            'name': 'Test Organization'
        }
    )

    assert response.status_code == response_code


def test_create_organization_success_response(
    admin_all_access_token_data: AccessTokenData,
    organizations_service_mock: Mock,
    organization: Organization
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    organizations_service_mock.create_organization.return_value = organization
    app.dependency_overrides[get_organizations_service] = lambda: organizations_service_mock

    response = test_client.post(
        '/v1/organizations', 
        json={
            'name': organization.name
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json['organization_id'] == str(organization.organization_id)
    assert response_json['name'] == organization.name
    assert response_json['created_at'] == organization.created_at.isoformat()
    assert response_json['updated_at'] == organization.updated_at.isoformat()


def test_create_organization_when_organization_exists(
    admin_all_access_token_data: AccessTokenData,
    organizations_service_mock: Mock,
    organization: Organization
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    organizations_service_mock.create_organization.side_effect = ValueError('Organization already exists')
    app.dependency_overrides[get_organizations_service] = lambda: organizations_service_mock

    response = test_client.post(
        '/v1/organizations', 
        json={
            'name': organization.name
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
