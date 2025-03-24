from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4
import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import get_access_token_data, get_api_key_access_scopes_helper, get_api_key_data, get_locations_service, get_hvac_dashboards_service, get_user_access_grants_helper
from app.v1.locations.schemas.location import Location
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.hvac_dashboards.schemas.hvac_dashboard import HvacDashboard


test_client = TestClient(app)


def test_create_hvac_dashboard_is_unauthorized_without_token():
    response = test_client.post('/v1/hvac-dashboards')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.HVAC_DASHBOARDS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.HVAC_DASHBOARDS_READ], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_hvac_dashboard_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    hvac_dashboards_service_mock: Mock,
    locations_service_mock: Mock
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock
    app.dependency_overrides[get_hvac_dashboards_service] = lambda: hvac_dashboards_service_mock

    response = test_client.post(
        '/v1/hvac-dashboards',
        json={
            'name': 'Test Hvac Dashboard',
            'location_id': str(uuid4())
        }
    )

    assert response.status_code == response_code
    

def test_create_hvac_dashboard_success_response(
    admin_all_access_token_data: AccessTokenData,
    hvac_dashboard: HvacDashboard,
    location: Location,
    hvac_dashboards_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    hvac_dashboards_service_mock.create_hvac_dashboard.return_value = hvac_dashboard
    app.dependency_overrides[get_hvac_dashboards_service] = lambda: hvac_dashboards_service_mock

    response = test_client.post(
        '/v1/hvac-dashboards',
        json={
            'name': hvac_dashboard.name,
            'location_id': str(location.location_id)
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'hvac_dashboard_id': str(hvac_dashboard.hvac_dashboard_id),
        'name': hvac_dashboard.name,
        'location_id': str(location.location_id),
        'created_at': hvac_dashboard.created_at.isoformat(),
        'updated_at': hvac_dashboard.updated_at.isoformat()
    }


def test_create_hvac_dashboard_when_location_doesnt_exist_for_jwt_auth(
    admin_all_access_token_data: AccessTokenData,
    hvac_dashboard: HvacDashboard,
    hvac_dashboards_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    locations_service_mock.get_location.return_value = None
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    app.dependency_overrides[get_hvac_dashboards_service] = lambda: hvac_dashboards_service_mock

    response = test_client.post(
        '/v1/hvac-dashboards',
        json={
            'name': hvac_dashboard.name,
            'location_id': str(uuid4())
        }
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_hvac_dashboard_when_location_doesnt_exist_for_api_auth(
    api_key: APIKey,
    hvac_dashboard: HvacDashboard,
    hvac_dashboards_service_mock: Mock,
    locations_service_mock: Mock,
    api_key_access_scopes_helper_mock: Mock
):
    app.dependency_overrides[get_api_key_data] = lambda: api_key

    api_key_access_scopes_helper_mock.get_all_access_scopes_for_api_key.return_value = [AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_WRITE]
    app.dependency_overrides[get_api_key_access_scopes_helper] = lambda: api_key_access_scopes_helper_mock

    locations_service_mock.get_location.return_value = None
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    app.dependency_overrides[get_hvac_dashboards_service] = lambda: hvac_dashboards_service_mock

    response = test_client.post(
        '/v1/hvac-dashboards',
        json={
            'name': hvac_dashboard.name,
            'location_id': str(uuid4())
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_hvac_dashboard_when_location_is_unauthorized(
    admin_all_access_token_data: AccessTokenData,
    hvac_dashboard: HvacDashboard,
    location: Location,
    hvac_dashboards_service_mock: Mock,
    user_access_grants_helper_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock
    app.dependency_overrides[get_hvac_dashboards_service] = lambda: hvac_dashboards_service_mock

    user_access_grants_helper_mock.is_user_authorized_for_location_write.return_value = False
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    response = test_client.post(
        '/v1/hvac-dashboards',
        json={
            'name': hvac_dashboard.name,
            'location_id': str(location.location_id)
        }
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN

