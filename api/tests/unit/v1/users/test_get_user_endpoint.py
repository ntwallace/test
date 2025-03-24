from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_users_service, get_access_token_data
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.users.schemas.user import User


test_client = TestClient(app)


def test_get_user_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/users/{uuid4()}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.USERS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.USERS_READ], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_get_user_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    user: User,
    users_service_mock: Mock,
    token_data_with_access_scopes: Callable,
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_users_service] = lambda: users_service_mock

    response = test_client.get(f'/v1/users/{user.user_id}')

    assert response.status_code == response_code


def test_get_user_success_response(
    admin_all_access_token_data: AccessTokenData,
    users_service_mock: Mock,
    user: User
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_users_service] = lambda: users_service_mock

    response = test_client.get(f'/v1/users/{user.user_id}')

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json['user_id'] == str(user.user_id)
    assert response_json['email'] == user.email
    assert response_json['first_name'] == user.first_name
    assert response_json['last_name'] == user.last_name
    assert response_json['created_at'] == user.created_at.isoformat()
    assert response_json['updated_at'] == user.updated_at.isoformat()


def test_get_user_when_user_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    users_service_mock: Mock,
    user: User
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    users_service_mock.get_user_by_user_id.return_value = None
    app.dependency_overrides[get_users_service] = lambda: users_service_mock

    response = test_client.get(f'/v1/users/{user.user_id}')

    assert response.status_code == status.HTTP_404_NOT_FOUND
