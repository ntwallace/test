from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4
import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import get_access_token_data, get_api_key_access_scopes_helper, get_api_key_data, get_locations_service, get_temperature_dashboards_service, get_user_access_grants_helper
from app.v1.locations.schemas.location import Location
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.temperature_dashboards.schemas.temperature_dashboard import TemperatureDashboard


test_client = TestClient(app)


def test_create_temperature_dashboard_is_unauthorized_without_token():
    response = test_client.post('/v1/temperature-dashboards')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.TEMPERATURE_DASHBOARDS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.TEMPERATURE_DASHBOARDS_READ], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_temperature_dashboard_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    temperature_dashboards_service_mock: Mock,
    locations_service_mock: Mock
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    response = test_client.post(
        '/v1/temperature-dashboards',
        json={
            'name': 'Test Temperature Dashboard',
            'location_id': str(uuid4())
        }
    )

    assert response.status_code == response_code
    

def test_create_temperature_dashboard_success_response(
    admin_all_access_token_data: AccessTokenData,
    temperature_dashboard: TemperatureDashboard,
    location: Location,
    temperature_dashboards_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    temperature_dashboards_service_mock.create_temperature_dashboard.return_value = temperature_dashboard
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    response = test_client.post(
        '/v1/temperature-dashboards',
        json={
            'name': temperature_dashboard.name,
            'location_id': str(location.location_id)
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'temperature_dashboard_id': str(temperature_dashboard.temperature_dashboard_id),
        'name': temperature_dashboard.name,
        'location_id': str(location.location_id),
        'created_at': temperature_dashboard.created_at.isoformat(),
        'updated_at': temperature_dashboard.updated_at.isoformat()
    }


def test_create_temperature_dashboard_when_location_doesnt_exist_for_jwt_auth(
    admin_all_access_token_data: AccessTokenData,
    temperature_dashboard: TemperatureDashboard,
    temperature_dashboards_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    locations_service_mock.get_location.return_value = None
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    response = test_client.post(
        '/v1/temperature-dashboards',
        json={
            'name': temperature_dashboard.name,
            'location_id': str(uuid4())
        }
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_temperature_dashboard_when_location_doesnt_exist_for_api_auth(
    api_key: APIKey,
    temperature_dashboard: TemperatureDashboard,
    temperature_dashboards_service_mock: Mock,
    locations_service_mock: Mock,
    api_key_access_scopes_helper_mock: Mock
):
    app.dependency_overrides[get_api_key_data] = lambda: api_key

    api_key_access_scopes_helper_mock.get_all_access_scopes_for_api_key.return_value = [AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_WRITE]
    app.dependency_overrides[get_api_key_access_scopes_helper] = lambda: api_key_access_scopes_helper_mock

    locations_service_mock.get_location.return_value = None
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    response = test_client.post(
        '/v1/temperature-dashboards',
        json={
            'name': temperature_dashboard.name,
            'location_id': str(uuid4())
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_temperature_dashboard_when_location_is_unauthorized(
    admin_all_access_token_data: AccessTokenData,
    temperature_dashboard: TemperatureDashboard,
    location: Location,
    temperature_dashboards_service_mock: Mock,
    user_access_grants_helper_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    user_access_grants_helper_mock.is_user_authorized_for_location_write.return_value = False
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    response = test_client.post(
        '/v1/temperature-dashboards',
        json={
            'name': temperature_dashboard.name,
            'location_id': str(location.location_id)
        }
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

