from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4
import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import get_access_token_data, get_api_key_access_scopes_helper, get_api_key_data, get_locations_service, get_temperature_dashboards_service, get_temperature_unit_widgets_service, get_user_access_grants_helper
from app.v1.locations.schemas.location import Location
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.temperature_dashboards.schemas.temperature_dashboard import TemperatureDashboard
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import TemperatureUnitWidget, TemperatureUnitWidgetCreate


test_client = TestClient(app)


def test_create_temperature_unit_widget_is_unauthorized_without_token():
    response = test_client.post('/v1/temperature-unit-widgets')
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
def test_create_temperature_unit_widget_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    temperature_unit_widgets_service_mock: Mock,
    temperature_dashboards_service_mock: Mock
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_temperature_unit_widgets_service] = lambda: temperature_unit_widgets_service_mock
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    response = test_client.post(
        '/v1/temperature-unit-widgets',
        json={
            'name': 'Test Temperature Unit Widget',
            'low_c': 20.0,
            'high_c': 30.0,
            'alert_threshold_s': 300,
            'appliance_type': 'Fridge',
            'temperature_sensor_place_id': str(uuid4()),
            'temperature_dashboard_id': str(uuid4())
        }
    )

    assert response.status_code == response_code


def test_create_temperature_unit_widget_success_response(
    admin_all_access_token_data: AccessTokenData,
    temperature_unit_widget: TemperatureUnitWidget,
    temperature_unit_widgets_service_mock: Mock,
    temperature_dashboards_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_temperature_unit_widgets_service] = lambda: temperature_unit_widgets_service_mock
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    response = test_client.post(
        '/v1/temperature-unit-widgets',
        json={
            'name': temperature_unit_widget.name,
            'low_c': temperature_unit_widget.low_c,
            'high_c': temperature_unit_widget.high_c,
            'alert_threshold_s': temperature_unit_widget.alert_threshold_s,
            'appliance_type': temperature_unit_widget.appliance_type,
            'temperature_sensor_place_id': str(temperature_unit_widget.temperature_sensor_place_id),
            'temperature_dashboard_id': str(temperature_unit_widget.temperature_dashboard_id)
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'temperature_unit_widget_id': str(temperature_unit_widget.temperature_unit_widget_id),
        'name': temperature_unit_widget.name,
        'low_c': temperature_unit_widget.low_c,
        'high_c': temperature_unit_widget.high_c,
        'alert_threshold_s': temperature_unit_widget.alert_threshold_s,
        'appliance_type': temperature_unit_widget.appliance_type,
        'temperature_sensor_place_id': str(temperature_unit_widget.temperature_sensor_place_id),
        'temperature_dashboard_id': str(temperature_unit_widget.temperature_dashboard_id),
        'created_at': temperature_unit_widget.created_at.isoformat(),
        'updated_at': temperature_unit_widget.updated_at.isoformat()
    }


def test_create_temperature_unit_widget_when_temperature_dashboard_doesnt_exist_for_jwt_auth(
    admin_all_access_token_data: AccessTokenData,
    temperature_unit_widget: TemperatureUnitWidget,
    temperature_unit_widgets_service_mock: Mock,
    temperature_dashboards_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_temperature_unit_widgets_service] = lambda: temperature_unit_widgets_service_mock
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    temperature_dashboards_service_mock.get_temperature_dashboard.return_value = None

    response = test_client.post(
        '/v1/temperature-unit-widgets',
        json={
            'name': temperature_unit_widget.name,
            'low_c': temperature_unit_widget.low_c,
            'high_c': temperature_unit_widget.high_c,
            'alert_threshold_s': temperature_unit_widget.alert_threshold_s,
            'appliance_type': temperature_unit_widget.appliance_type,
            'temperature_sensor_place_id': str(temperature_unit_widget.temperature_sensor_place_id),
            'temperature_dashboard_id': str(temperature_unit_widget.temperature_dashboard_id)
        }
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_create_temperature_unit_widget_when_temperature_dashboard_doesnt_exist_for_api_key_auth(
    api_key: APIKey,
    temperature_unit_widget: TemperatureUnitWidget,
    temperature_unit_widgets_service_mock: Mock,
    temperature_dashboards_service_mock: Mock,
    api_key_access_scopes_helper_mock: Mock
):
    app.dependency_overrides[get_api_key_data] = lambda: api_key

    api_key_access_scopes_helper_mock.get_all_access_scopes_for_api_key.return_value = [AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_WRITE]
    app.dependency_overrides[get_api_key_access_scopes_helper] = lambda: api_key_access_scopes_helper_mock

    app.dependency_overrides[get_temperature_unit_widgets_service] = lambda: temperature_unit_widgets_service_mock
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    temperature_dashboards_service_mock.get_temperature_dashboard.return_value = None

    response = test_client.post(
        '/v1/temperature-unit-widgets',
        json={
            'name': temperature_unit_widget.name,
            'low_c': temperature_unit_widget.low_c,
            'high_c': temperature_unit_widget.high_c,
            'alert_threshold_s': temperature_unit_widget.alert_threshold_s,
            'appliance_type': temperature_unit_widget.appliance_type,
            'temperature_sensor_place_id': str(temperature_unit_widget.temperature_sensor_place_id),
            'temperature_dashboard_id': str(temperature_unit_widget.temperature_dashboard_id)
        }
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_temperature_unit_widget_when_temperature_dashboard_is_unauthorized(
    admin_all_access_token_data: AccessTokenData,
    temperature_unit_widget: TemperatureUnitWidget,
    temperature_unit_widgets_service_mock: Mock,
    temperature_dashboards_service_mock: Mock,
    user_access_grants_helper_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_temperature_unit_widgets_service] = lambda: temperature_unit_widgets_service_mock
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    user_access_grants_helper_mock.is_user_authorized_for_location_write.return_value = False
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    response = test_client.post(
        '/v1/temperature-unit-widgets',
        json={
            'name': temperature_unit_widget.name,
            'low_c': temperature_unit_widget.low_c,
            'high_c': temperature_unit_widget.high_c,
            'alert_threshold_s': temperature_unit_widget.alert_threshold_s,
            'appliance_type': temperature_unit_widget.appliance_type,
            'temperature_sensor_place_id': str(temperature_unit_widget.temperature_sensor_place_id),
            'temperature_dashboard_id': str(temperature_unit_widget.temperature_dashboard_id)
        }
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
