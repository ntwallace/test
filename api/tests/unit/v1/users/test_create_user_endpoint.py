from typing import Callable, List
from unittest.mock import Mock

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_users_service, get_access_token_data
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.users.schemas.user import User


test_client = TestClient(app)


def test_create_user_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post('/v1/users')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.USERS_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.USERS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.USERS_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_user_access_scope_responses(access_scopes: List[AccessScope],
                                            response_code: int,
                                            token_data_with_access_scopes: Callable,
                                            users_service_mock: Mock):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    users_service_mock.get_user_by_email.return_value = None
    app.dependency_overrides[get_users_service] = lambda: users_service_mock

    response = test_client.post(
        '/v1/users', 
        json={
            'email': 'admin@powerx.co',
            'first_name': 'Lando',
            'last_name': 'Norris',
            'password': 'password'
        }
    )

    assert response.status_code == response_code


def test_create_user_success_response(admin_all_access_token_data: AccessTokenData,
                                      users_service_mock: Mock,
                                      user: User):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    users_service_mock.get_user_by_email.return_value = None
    app.dependency_overrides[get_users_service] = lambda: users_service_mock

    response = test_client.post(
        '/v1/users',
        json={
            'email': 'admin@powerx.co',
            'first_name': 'Lando',
            'last_name': 'Norris',
            'password': 'password'
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json['user_id'] == str(user.user_id)
    assert response_json['email'] == user.email
    assert response_json['first_name'] == user.first_name
    assert response_json['last_name'] == user.last_name
    assert response_json['created_at'] == user.created_at.isoformat()
    assert response_json['updated_at'] == user.updated_at.isoformat()


def test_create_user_when_user_exists(admin_all_access_token_data: AccessTokenData,
                                      users_service_mock: Mock,
                                      user: User):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_users_service] = lambda: users_service_mock

    response = test_client.post(
        '/v1/users',
        json={
            'email': 'admin@powerx.co',
            'first_name': 'Lando',
            'last_name': 'Norris',
            'password': 'password'
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
