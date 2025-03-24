from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_organization_users_service, get_organizations_service, get_access_token_data
from app.v1.organizations.schemas.organization_user import OrganizationUser
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.organizations.schemas.organization import Organization


test_client = TestClient(app)


def test_create_organization_user_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post(f'/v1/organizations/{uuid4()}/users')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ORGANIZATIONS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ORGANIZATIONS_READ], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ORGANIZATION_USERS_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.ORGANIZATION_USERS_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_organization_user_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    organizations_service_mock: Mock,
    organization_users_service_mock: Mock,
    organization: Organization,
    organization_user: OrganizationUser,
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    organizations_service_mock.get_organization_by_organization_id.return_value = organization
    app.dependency_overrides[get_organizations_service] = lambda: organizations_service_mock

    organization_users_service_mock.get_organization_user.return_value = None
    organization_users_service_mock.create_organization_user.return_value = organization_user
    app.dependency_overrides[get_organization_users_service] = lambda: organization_users_service_mock

    response = test_client.post(
        f'/v1/organizations/{organization_user.organization_id}/users',
        json={
            'organization_id': str(organization_user.organization_id),
            'user_id': str(organization_user.user_id)
        }
    )

    assert response.status_code == response_code


def test_create_organization_user_success_response(
    admin_all_access_token_data: AccessTokenData,
    organization_users_service_mock: Mock,
    organizations_service_mock: Mock,
    organization_user: OrganizationUser
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    app.dependency_overrides[get_organizations_service] = lambda: organizations_service_mock

    organization_users_service_mock.get_organization_user.return_value = None
    organization_users_service_mock.create_organization_user.return_value = organization_user
    app.dependency_overrides[get_organization_users_service] = lambda: organization_users_service_mock

    response = test_client.post(
        f'/v1/organizations/{organization_user.organization_id}/users',
        json={
            'organization_id': str(organization_user.organization_id),
            'user_id': str(organization_user.user_id)
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json['organization_id'] == str(organization_user.organization_id)
    assert response_json['user_id'] == str(organization_user.user_id)
    assert response_json['created_at'] == organization_user.created_at.isoformat()


def test_create_organization_user_when_organization_user_exists(
    admin_all_access_token_data: AccessTokenData,
    organization_users_service_mock: Mock,
    organizations_service_mock: Mock,
    organization_user: OrganizationUser
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    
    app.dependency_overrides[get_organizations_service] = lambda: organizations_service_mock

    organization_users_service_mock.get_organization_user.return_value = organization_user
    app.dependency_overrides[get_organization_users_service] = lambda: organization_users_service_mock

    response = test_client.post(
        f'/v1/organizations/{organization_user.organization_id}/users',
        json={
            'organization_id': str(organization_user.organization_id),
            'user_id': str(organization_user.user_id)
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_organization_user_when_organization_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    organizations_service_mock: Mock,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    
    organizations_service_mock.get_organization_by_organization_id.return_value = None
    app.dependency_overrides[get_organizations_service] = lambda: organizations_service_mock

    response = test_client.post(
        f'/v1/organizations/{uuid4()}/users',
        json={
            'organization_id': str(uuid4()),
            'user_id': str(uuid4())
        }
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
