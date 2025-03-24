from typing import Callable, List
from unittest.mock import Mock

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_access_token_data, get_organizations_service
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.organizations.schemas.organization import Organization


test_client = TestClient(app)


def test_get_organization_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get('/v1/organizations')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.ORGANIZATIONS_READ], status.HTTP_200_OK),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ORGANIZATIONS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ORGANIZATIONS_READ], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ORGANIZATION_USERS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ORGANIZATION_USERS_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_get_organizations_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    organizations_service_mock: Mock
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    organizations_service_mock.get_organizations.return_value = []
    app.dependency_overrides[get_organizations_service] = lambda: organizations_service_mock

    response = test_client.get('/v1/organizations')

    assert response.status_code == response_code


def test_get_organizations_success_response(
    admin_all_access_token_data: AccessTokenData,
    organizations_service_mock: Mock,
    organization: Organization
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    organizations_service_mock.get_organizations.return_value = [organization]
    app.dependency_overrides[get_organizations_service] = lambda: organizations_service_mock

    response = test_client.get('/v1/organizations')

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 1
    response_json_organization = response_json[0]
    assert response_json_organization['organization_id'] == str(organization.organization_id)
    assert response_json_organization['name'] == organization.name
    assert response_json_organization['created_at'] == organization.created_at.isoformat()
    assert response_json_organization['updated_at'] == organization.updated_at.isoformat()


def test_get_organizations_filter_by_name_success_response(
    admin_all_access_token_data: AccessTokenData,
    organizations_service_mock: Mock,
    organization: Organization
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    organizations_service_mock.get_organizations.return_value = [organization,]
    app.dependency_overrides[get_organizations_service] = lambda: organizations_service_mock

    response = test_client.get('/v1/organizations?name=test')

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 1
    response_json_organization = response_json[0]
    assert response_json_organization['organization_id'] == str(organization.organization_id)
    assert response_json_organization['name'] == organization.name
    assert response_json_organization['created_at'] == organization.created_at.isoformat()
    assert response_json_organization['updated_at'] == organization.updated_at.isoformat()

def test_get_organizations_empty_response(
    admin_all_access_token_data: AccessTokenData,
    organizations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    organizations_service_mock.get_organizations.return_value = []
    app.dependency_overrides[get_organizations_service] = lambda: organizations_service_mock

    response = test_client.get('/v1/organizations')

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert len(response_json) == 0
