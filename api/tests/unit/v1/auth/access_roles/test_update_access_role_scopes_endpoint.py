from typing import List, Callable
from unittest.mock import Mock
from uuid import UUID

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.auth.schemas.access_role import AccessRole
from app.v1.auth.schemas.access_role_access_scope import AccessRoleAccessScope
from app.v1.dependencies import get_access_roles_service, get_access_role_access_scopes_service, get_access_token_data
from app.v1.schemas import AccessScope


test_client = TestClient(app)


def test_update_access_role_access_scopes_unauthorized(sample_access_role_id):
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.put(f'/v1/auth/access-roles/{sample_access_role_id}/access-scopes')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_200_OK),
        ([AccessScope.LOCATIONS_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_update_access_role_access_scopes_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    mock_access_roles_service: Mock,
    mock_access_role_access_scopes_service: Mock,
    sample_access_role: AccessRole,
    sample_access_role_id: UUID,
    sample_access_role_access_scope: AccessRoleAccessScope
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_access_roles_service] = lambda: mock_access_roles_service
    app.dependency_overrides[get_access_role_access_scopes_service] = lambda: mock_access_role_access_scopes_service
    mock_access_roles_service.get_access_role.return_value = sample_access_role
    mock_access_role_access_scopes_service.update_access_role_access_scopes.return_value = [sample_access_role_access_scope]
    new_scopes = [AccessScope.ADMIN]

    response = test_client.put(
        f'/v1/auth/access-roles/{sample_access_role_id}/access-scopes',
        json=new_scopes
    )

    assert response.status_code == response_code


def test_update_access_role_access_scopes_success(
    mock_access_roles_service,
    mock_access_role_access_scopes_service,
    admin_all_access_token_data,
    sample_access_role,
    sample_access_role_id,
    sample_access_role_access_scope
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_access_roles_service] = lambda: mock_access_roles_service
    app.dependency_overrides[get_access_role_access_scopes_service] = lambda: mock_access_role_access_scopes_service
    mock_access_roles_service.get_access_role.return_value = sample_access_role
    mock_access_role_access_scopes_service.update_access_role_access_scopes.return_value = [sample_access_role_access_scope]
    new_scopes = [AccessScope.ADMIN]

    response = test_client.put(
        f'/v1/auth/access-roles/{sample_access_role_id}/access-scopes',
        json=new_scopes
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == new_scopes
    mock_access_roles_service.get_access_role.assert_called_once_with(sample_access_role_id)
    mock_access_role_access_scopes_service.update_access_role_access_scopes.assert_called_once_with(
        sample_access_role_id,
        new_scopes
    )


def test_update_access_role_access_scopes_not_found(
    mock_access_roles_service,
    mock_access_role_access_scopes_service,
    admin_all_access_token_data,
    sample_access_role_id
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_access_roles_service] = lambda: mock_access_roles_service
    app.dependency_overrides[get_access_role_access_scopes_service] = lambda: mock_access_role_access_scopes_service
    mock_access_roles_service.get_access_role.return_value = None
    new_scopes = [AccessScope.ADMIN]

    response = test_client.put(
        f'/v1/auth/access-roles/{sample_access_role_id}/access-scopes',
        json=new_scopes
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()['detail'] == 'Access role not found'
    mock_access_role_access_scopes_service.update_access_role_access_scopes.assert_not_called()