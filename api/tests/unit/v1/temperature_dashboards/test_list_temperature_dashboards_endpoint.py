from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4
import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_access_token_data, get_temperature_dashboards_service, get_locations_service, get_user_access_grants_helper
from app.v1.temperature_dashboards.schemas.temperature_dashboard import TemperatureDashboard
from app.v1.schemas import AccessScope


test_client = TestClient(app)


def test_list_temperature_dashboard_is_unauthorized_without_token():
    response = test_client.get('/v1/temperature-dashboards')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([], status.HTTP_403_FORBIDDEN),
        ([AccessScope.TEMPERATURE_DASHBOARDS_READ], status.HTTP_200_OK),
        ([AccessScope.TEMPERATURE_DASHBOARDS_WRITE], status.HTTP_403_FORBIDDEN),
    ]
)
def test_list_temperature_dashboard_access_scope_responses(
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

    response = test_client.get('/v1/temperature-dashboards')

    assert response.status_code == response_code


def test_list_temperature_dashboard_success_response(
    temperature_dashboard: TemperatureDashboard,
    token_data_with_access_scopes: Callable,
    temperature_dashboards_service_mock: Mock,
    locations_service_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    temperature_dashboards_service_mock.filter_by.return_value = [temperature_dashboard, ]
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock


    response = test_client.get('/v1/temperature-dashboards')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'temperature_dashboard_id': str(temperature_dashboard.temperature_dashboard_id),
            'name': temperature_dashboard.name,
            'location_id': str(temperature_dashboard.location_id),
            'created_at': temperature_dashboard.created_at.isoformat(),
            'updated_at': temperature_dashboard.updated_at.isoformat()
        }
    ]


def test_list_temperature_dashboard_empty_response(
    admin_all_access_token_data: Callable,
    temperature_dashboards_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    temperature_dashboards_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    response = test_client.get('/v1/temperature-dashboards')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_temperature_dashboard_returns_only_authorized_resources(
    temperature_dashboard: TemperatureDashboard,
    token_data_with_access_scopes: Callable,
    temperature_dashboards_service_mock: Mock,
    locations_service_mock: Mock,
    user_access_grants_helper_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    user_access_grants_helper_mock.is_user_authorized_for_location_read.side_effect = [True, False]
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    temperature_dashboards_service_mock.filter_by.return_value = [
        temperature_dashboard,
        TemperatureDashboard(
            temperature_dashboard_id=uuid4(),
            name='Test Dashboard 2',
            location_id=uuid4(),
            created_at=temperature_dashboard.created_at,
            updated_at=temperature_dashboard.updated_at
        )
    ]
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    response = test_client.get('/v1/temperature-dashboards')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'temperature_dashboard_id': str(temperature_dashboard.temperature_dashboard_id),
            'name': temperature_dashboard.name,
            'location_id': str(temperature_dashboard.location_id),
            'created_at': temperature_dashboard.created_at.isoformat(),
            'updated_at': temperature_dashboard.updated_at.isoformat()
        }
    ]
