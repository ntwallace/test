from typing import List, Callable
from unittest.mock import Mock
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.auth.schemas.access_role import AccessRole
from app.v1.dependencies import get_access_roles_service, get_access_token_data
from app.v1.schemas import AccessScope


test_client = TestClient(app)


def test_get_access_role_unauthorized(sample_access_role_id):
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/auth/access-roles/{sample_access_role_id}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_200_OK),
        ([AccessScope.LOCATIONS_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_get_access_role_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    mock_access_roles_service: Mock,
    sample_access_role: AccessRole,
    sample_access_role_id: UUID
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_access_roles_service] = lambda: mock_access_roles_service
    mock_access_roles_service.get_access_role.return_value = sample_access_role

    response = test_client.get(f'/v1/auth/access-roles/{sample_access_role_id}')

    assert response.status_code == response_code


def test_get_access_role_success(mock_access_roles_service, admin_all_access_token_data, sample_access_role, sample_access_role_id):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_access_roles_service] = lambda: mock_access_roles_service
    mock_access_roles_service.get_access_role.return_value = sample_access_role

    response = test_client.get(f'/v1/auth/access-roles/{sample_access_role_id}')

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data['access_role_id'] == str(sample_access_role.access_role_id)
    assert response_data['name'] == sample_access_role.name


def test_get_access_role_not_found(mock_access_roles_service, admin_all_access_token_data, sample_access_role_id):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_access_roles_service] = lambda: mock_access_roles_service
    mock_access_roles_service.get_access_role.return_value = None

    response = test_client.get(f'/v1/auth/access-roles/{sample_access_role_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Access role not found'