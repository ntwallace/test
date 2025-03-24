from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4
import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_access_token_data, get_electricity_dashboards_service, get_locations_service
from app.v1.electricity_dashboards.schemas.electricity_dashboard import ElectricityDashboard
from app.v1.schemas import AccessScope


test_client = TestClient(app)


def test_list_electricity_dashboard_is_unauthorized_without_token():
    response = test_client.get('/v1/electricity-dashboards')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ELECTRICITY_DASHBOARDS_READ], status.HTTP_200_OK),
        ([AccessScope.ELECTRICITY_DASHBOARDS_WRITE], status.HTTP_403_FORBIDDEN),
    ]
)
def test_list_electricity_dashboard_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    electricity_dashboards_service_mock: Mock,
    locations_service_mock: Mock
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock
    app.dependency_overrides[get_electricity_dashboards_service] = lambda: electricity_dashboards_service_mock

    response = test_client.get('/v1/electricity-dashboards')

    assert response.status_code == response_code


def test_list_electricity_dashboard_success_response(
    electricity_dashboard: ElectricityDashboard,
    token_data_with_access_scopes: Callable,
    electricity_dashboards_service_mock: Mock,
    locations_service_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.ELECTRICITY_DASHBOARDS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    electricity_dashboards_service_mock.filter_by.return_value = [electricity_dashboard, ]
    app.dependency_overrides[get_electricity_dashboards_service] = lambda: electricity_dashboards_service_mock


    response = test_client.get('/v1/electricity-dashboards')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'electricity_dashboard_id': str(electricity_dashboard.electricity_dashboard_id),
            'name': electricity_dashboard.name,
            'location_id': str(electricity_dashboard.location_id),
            'created_at': electricity_dashboard.created_at.isoformat(),
            'updated_at': electricity_dashboard.updated_at.isoformat()
        }
    ]


def test_list_electricity_dashboard_empty_response(
    admin_all_access_token_data: Callable,
    electricity_dashboards_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    electricity_dashboards_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_electricity_dashboards_service] = lambda: electricity_dashboards_service_mock

    response = test_client.get('/v1/electricity-dashboards')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_electricity_dashboard_returns_only_authorized_resources(
    electricity_dashboard: ElectricityDashboard,
    token_data_with_access_scopes: Callable,
    electricity_dashboards_service_mock: Mock,
    locations_service_mock: Mock,
    user_access_grants_helper_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.ELECTRICITY_DASHBOARDS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    user_access_grants_helper_mock.is_user_authorized_for_location_read.side_effect = [True, False]

    electricity_dashboards_service_mock.filter_by.return_value = [
        electricity_dashboard,
        ElectricityDashboard(
            electricity_dashboard_id=uuid4(),
            name='Test Dashboard 2',
            location_id=uuid4(),
            created_at=electricity_dashboard.created_at,
            updated_at=electricity_dashboard.updated_at
        )
    ]
    app.dependency_overrides[get_electricity_dashboards_service] = lambda: electricity_dashboards_service_mock

    response = test_client.get('/v1/electricity-dashboards')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'electricity_dashboard_id': str(electricity_dashboard.electricity_dashboard_id),
            'name': electricity_dashboard.name,
            'location_id': str(electricity_dashboard.location_id),
            'created_at': electricity_dashboard.created_at.isoformat(),
            'updated_at': electricity_dashboard.updated_at.isoformat()
        }
    ]
