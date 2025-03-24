from typing import List, Callable
from unittest.mock import Mock
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.auth.schemas.access_role import AccessRole
from app.v1.dependencies import (
    get_access_roles_service,
    get_user_access_roles_service,
    get_access_token_data,
    get_users_service
)
from app.v1.schemas import AccessScope
from app.v1.users.schemas.user import User


test_client = TestClient(app)


def test_remove_access_role_from_user_unauthorized(sample_user_id: UUID, sample_access_role_id: UUID):
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.delete(f'/v1/auth/users/{sample_user_id}/access-roles/{sample_access_role_id}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_204_NO_CONTENT),
        ([AccessScope.USERS_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_remove_access_role_from_user_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    mock_users_service: Mock,
    mock_access_roles_service: Mock,
    mock_user_access_roles_service: Mock,
    sample_user_id: UUID,
    sample_access_role_id: UUID,
    sample_user: User,
    sample_access_role: AccessRole
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_users_service] = lambda: mock_users_service
    app.dependency_overrides[get_access_roles_service] = lambda: mock_access_roles_service
    app.dependency_overrides[get_user_access_roles_service] = lambda: mock_user_access_roles_service

    mock_users_service.get_user_by_user_id.return_value = sample_user
    mock_access_roles_service.get_access_role.return_value = sample_access_role

    response = test_client.delete(f'/v1/auth/users/{sample_user_id}/access-roles/{sample_access_role_id}')

    assert response.status_code == response_code


def test_remove_access_role_from_user_success(
    mock_users_service: Mock,
    mock_access_roles_service: Mock,
    mock_user_access_roles_service: Mock,
    admin_all_access_token_data,
    sample_user_id: UUID,
    sample_access_role_id: UUID,
    sample_user: User,
    sample_access_role: AccessRole
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_users_service] = lambda: mock_users_service
    app.dependency_overrides[get_access_roles_service] = lambda: mock_access_roles_service
    app.dependency_overrides[get_user_access_roles_service] = lambda: mock_user_access_roles_service

    mock_users_service.get_user_by_user_id.return_value = sample_user
    mock_access_roles_service.get_access_role.return_value = sample_access_role

    response = test_client.delete(f'/v1/auth/users/{sample_user_id}/access-roles/{sample_access_role_id}')

    assert response.status_code == status.HTTP_204_NO_CONTENT
    mock_user_access_roles_service.delete_user_access_role.assert_called_once_with(sample_user_id, sample_access_role_id)


def test_remove_access_role_from_user_not_found(
    mock_users_service: Mock,
    mock_access_roles_service: Mock,
    mock_user_access_roles_service: Mock,
    admin_all_access_token_data,
    sample_user_id: UUID,
    sample_access_role_id: UUID
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_users_service] = lambda: mock_users_service
    app.dependency_overrides[get_access_roles_service] = lambda: mock_access_roles_service
    app.dependency_overrides[get_user_access_roles_service] = lambda: mock_user_access_roles_service

    mock_users_service.get_user_by_user_id.return_value = None

    response = test_client.delete(f'/v1/auth/users/{sample_user_id}/access-roles/{sample_access_role_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'User not found'


def test_remove_access_role_from_user_role_not_found(
    mock_users_service: Mock,
    mock_access_roles_service: Mock,
    mock_user_access_roles_service: Mock,
    admin_all_access_token_data,
    sample_user_id: UUID,
    sample_access_role_id: UUID,
    sample_user: User
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_users_service] = lambda: mock_users_service
    app.dependency_overrides[get_access_roles_service] = lambda: mock_access_roles_service
    app.dependency_overrides[get_user_access_roles_service] = lambda: mock_user_access_roles_service

    mock_users_service.get_user_by_user_id.return_value = sample_user
    mock_access_roles_service.get_access_role.return_value = None

    response = test_client.delete(f'/v1/auth/users/{sample_user_id}/access-roles/{sample_access_role_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Access role not found' 