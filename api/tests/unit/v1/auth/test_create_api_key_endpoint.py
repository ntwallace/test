from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4
from fastapi import status
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import get_access_token_data, get_api_keys_service
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_create_api_key_sensor_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post('/v1/auth/api-keys')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_201_CREATED),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_api_key_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    api_keys_service_mock: Mock,
    api_key: APIKey
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    api_keys_service_mock.create_api_key.return_value = ('asdfasdf', api_key)
    app.dependency_overrides[get_api_keys_service] = lambda: api_keys_service_mock

    response = test_client.post('/v1/auth/api-keys', json={
        'name': api_key.name,
    })

    assert response.status_code == response_code


def test_create_api_key_success_response(
    admin_all_access_token_data: AccessTokenData,
    api_keys_service_mock: Mock,
    api_key: APIKey
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    api_keys_service_mock.create_api_key.return_value = ('asdfasdf', api_key)
    app.dependency_overrides[get_api_keys_service] = lambda: api_keys_service_mock

    response = test_client.post('/v1/auth/api-keys', json={
        'name': api_key.name,
    })

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'api_key_id': str(api_key.api_key_id),
        'name': api_key.name,
        'api_key': 'asdfasdf',
        'created_at': api_key.created_at.isoformat(),
        'updated_at': api_key.updated_at.isoformat()
    }


def test_create_api_key_when_api_key_already_exists(
    admin_all_access_token_data: AccessTokenData,
    api_keys_service_mock: Mock,
    api_key: APIKey
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    api_keys_service_mock.create_api_key.side_effect = ValueError('API key already exists')
    app.dependency_overrides[get_api_keys_service] = lambda: api_keys_service_mock

    response = test_client.post('/v1/auth/api-keys', json={
        'name': api_key.name,
    })

    assert response.status_code == status.HTTP_400_BAD_REQUEST
