from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4
import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_access_token_data, get_hvac_dashboards_service, get_locations_service, get_user_access_grants_helper
from app.v1.hvac_dashboards.schemas.hvac_dashboard import HvacDashboard
from app.v1.schemas import AccessScope


test_client = TestClient(app)


def test_list_hvac_dashboard_is_unauthorized_without_token():
    response = test_client.get('/v1/hvac-dashboards')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_READ], status.HTTP_200_OK),
        ([AccessScope.HVAC_DASHBOARDS_READ], status.HTTP_403_FORBIDDEN),
        ([AccessScope.HVAC_DASHBOARDS_WRITE], status.HTTP_403_FORBIDDEN),
    ]
)
def test_list_hvac_dashboard_access_scope_responses(
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

    response = test_client.get('/v1/hvac-dashboards')

    assert response.status_code == response_code


def test_list_hvac_dashboard_success_response(
    hvac_dashboard: HvacDashboard,
    token_data_with_access_scopes: Callable,
    hvac_dashboards_service_mock: Mock,
    locations_service_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    hvac_dashboards_service_mock.filter_by.return_value = [hvac_dashboard, ]
    app.dependency_overrides[get_hvac_dashboards_service] = lambda: hvac_dashboards_service_mock


    response = test_client.get('/v1/hvac-dashboards')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'hvac_dashboard_id': str(hvac_dashboard.hvac_dashboard_id),
            'name': hvac_dashboard.name,
            'location_id': str(hvac_dashboard.location_id),
            'created_at': hvac_dashboard.created_at.isoformat(),
            'updated_at': hvac_dashboard.updated_at.isoformat()
        }
    ]


def test_list_hvac_dashboard_empty_response(
    admin_all_access_token_data: Callable,
    hvac_dashboards_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    hvac_dashboards_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_hvac_dashboards_service] = lambda: hvac_dashboards_service_mock

    response = test_client.get('/v1/hvac-dashboards')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_hvac_dashboard_returns_only_authorized_resources(
    hvac_dashboard: HvacDashboard,
    token_data_with_access_scopes: Callable,
    hvac_dashboards_service_mock: Mock,
    locations_service_mock: Mock,
    user_access_grants_helper_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    user_access_grants_helper_mock.is_user_authorized_for_location_read.side_effect = [True, False]
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    hvac_dashboards_service_mock.filter_by.return_value = [
        hvac_dashboard,
        HvacDashboard(
            hvac_dashboard_id=uuid4(),
            name='Test Dashboard 2',
            location_id=uuid4(),
            created_at=hvac_dashboard.created_at,
            updated_at=hvac_dashboard.updated_at
        )
    ]
    app.dependency_overrides[get_hvac_dashboards_service] = lambda: hvac_dashboards_service_mock

    response = test_client.get('/v1/hvac-dashboards')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'hvac_dashboard_id': str(hvac_dashboard.hvac_dashboard_id),
            'name': hvac_dashboard.name,
            'location_id': str(hvac_dashboard.location_id),
            'created_at': hvac_dashboard.created_at.isoformat(),
            'updated_at': hvac_dashboard.updated_at.isoformat()
        }
    ]
