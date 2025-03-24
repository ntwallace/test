from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4, UUID

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_locations_service, get_organization_users_service, get_users_service, get_user_access_scopes_helper
from app.v1.locations.schemas.location import Location
from app.v1.organizations.models.organization import Organization
from app.v1.schemas import AccessScope
from app.v1.users.schemas.user import User
from app.v1.utils import hash_password

test_client = TestClient(app)


def test_refresh_success_response(
    users_service_mock: Mock,
    organization_users_service_mock: Mock,
    locations_service_mock: Mock,
    user_access_scopes_helper_mock: Mock,
    organization: Organization,
    location: Location
):
    users_service_mock.get_user_by_email.return_value = User(
        user_id=uuid4(),
        first_name='Lando',
        last_name='Norris',
        email='test@powerx.co',
        created_at=datetime.now(),
        updated_at=datetime.now(),
        password_hash=hash_password('password')
    )
    app.dependency_overrides[get_users_service] = lambda: users_service_mock

    organization_users_service_mock.get_organizations_for_user.return_value = [organization,]
    app.dependency_overrides[get_organization_users_service] = lambda: organization_users_service_mock

    locations_service_mock.get_locations_by_organization_id.return_value = [location,]
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    user_access_scopes_helper_mock.get_all_access_scopes_for_user.return_value = [AccessScope.ADMIN]
    app.dependency_overrides[get_user_access_scopes_helper] = lambda: user_access_scopes_helper_mock

    response = test_client.post(
        '/v1/auth/login',
        data={
            'username': 'test@powerx.co',
            'password': 'password'
        }
    )
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    refresh_token = response.json()['refresh_token']

    response = test_client.post(
        '/v1/auth/refresh',
        headers={
            'Authorization': f'Bearer {refresh_token}'
        }
    )

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert 'access_token' in response_json
    assert response_json['token_type'] == 'bearer'


