from datetime import datetime
from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4
import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_access_token_data, get_temperature_dashboards_service, get_temperature_unit_widgets_service, get_user_access_grants_helper
from app.v1.temperature_dashboards.schemas.temperature_dashboard import TemperatureDashboard
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import ApplianceType, TemperatureUnitWidget
from app.v1.schemas import AccessScope


test_client = TestClient(app)


def test_list_temperature_unit_widgets_is_unauthorized_without_token():
    response = test_client.get('/v1/temperature-unit-widgets')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_READ], status.HTTP_200_OK),
        ([AccessScope.TEMPERATURE_DASHBOARDS_READ], status.HTTP_403_FORBIDDEN),
        ([AccessScope.TEMPERATURE_DASHBOARDS_WRITE], status.HTTP_403_FORBIDDEN),
    ]
)
def test_list_temperature_unit_widgets_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    temperature_unit_widgets_service_mock: Mock,
    temperature_dashboards_service_mock: Mock
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock
    app.dependency_overrides[get_temperature_unit_widgets_service] = lambda: temperature_unit_widgets_service_mock

    response = test_client.get('/v1/temperature-unit-widgets')

    assert response.status_code == response_code


def test_list_temperature_unit_widgets_success_response(
    temperature_unit_widget: TemperatureUnitWidget,
    token_data_with_access_scopes: Callable,
    temperature_unit_widgets_service_mock: Mock,
    temperature_dashboards_service_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    temperature_unit_widgets_service_mock.filter_by.return_value = [temperature_unit_widget, ]
    app.dependency_overrides[get_temperature_unit_widgets_service] = lambda: temperature_unit_widgets_service_mock

    response = test_client.get('/v1/temperature-unit-widgets')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'temperature_unit_widget_id': str(temperature_unit_widget.temperature_unit_widget_id),
        'name': temperature_unit_widget.name,
        'low_c': temperature_unit_widget.low_c,
        'high_c': temperature_unit_widget.high_c,
        'alert_threshold_s': temperature_unit_widget.alert_threshold_s,
        'appliance_type': str(temperature_unit_widget.appliance_type),
        'temperature_sensor_place_id': str(temperature_unit_widget.temperature_sensor_place_id),
        'temperature_dashboard_id': str(temperature_unit_widget.temperature_dashboard_id),
        'created_at': temperature_unit_widget.created_at.isoformat(),
        'updated_at': temperature_unit_widget.updated_at.isoformat()
    }]


def test_list_temperature_unit_widgets_empty_response(
    token_data_with_access_scopes: Callable,
    temperature_unit_widgets_service_mock: Mock,
    temperature_dashboards_service_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    temperature_unit_widgets_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_temperature_unit_widgets_service] = lambda: temperature_unit_widgets_service_mock

    response = test_client.get('/v1/temperature-unit-widgets')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_temperature_unit_widgets_returns_only_authorized_resources(
    token_data_with_access_scopes: Callable,
    temperature_unit_widget: TemperatureUnitWidget,
    temperature_unit_widgets_service_mock: Mock,
    temperature_dashboards_service_mock: Mock,
    user_access_grants_helper_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    user_access_grants_helper_mock.is_user_authorized_for_location_read.side_effect = [True, False]
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    temperature_unit_widgets_service_mock.filter_by.return_value = [
        temperature_unit_widget,
        TemperatureUnitWidget(
            temperature_unit_widget_id=uuid4(),
            name='Test Temperature Unit Widget',
            low_c=20.0,
            high_c=30.0,
            alert_threshold_s=300,
            appliance_type=ApplianceType.FRIDGE,
            temperature_sensor_place_id=uuid4(),
            temperature_dashboard_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    ]
    app.dependency_overrides[get_temperature_unit_widgets_service] = lambda: temperature_unit_widgets_service_mock

    response = test_client.get('/v1/temperature-unit-widgets')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'temperature_unit_widget_id': str(temperature_unit_widget.temperature_unit_widget_id),
        'name': temperature_unit_widget.name,
        'low_c': temperature_unit_widget.low_c,
        'high_c': temperature_unit_widget.high_c,
        'alert_threshold_s': temperature_unit_widget.alert_threshold_s,
        'appliance_type': str(temperature_unit_widget.appliance_type),
        'temperature_sensor_place_id': str(temperature_unit_widget.temperature_sensor_place_id),
        'temperature_dashboard_id': str(temperature_unit_widget.temperature_dashboard_id),
        'created_at': temperature_unit_widget.created_at.isoformat(),
        'updated_at': temperature_unit_widget.updated_at.isoformat()
    }]


def test_list_temperature_unit_widgets_parses_query_parameters(
    token_data_with_access_scopes: Callable,
    temperature_unit_widget: TemperatureUnitWidget,
    temperature_unit_widgets_service_mock: Mock,
    temperature_dashboards_service_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.TEMPERATURE_DASHBOARDS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_temperature_dashboards_service] = lambda: temperature_dashboards_service_mock

    temperature_unit_widgets_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_temperature_unit_widgets_service] = lambda: temperature_unit_widgets_service_mock

    response = test_client.get('/v1/temperature-unit-widgets?name=Test&appliance=Fridge&lower_temperature_c=1&upper_temperature_c=2&alert_threshold_s=3')

    temperature_unit_widgets_service_mock.filter_by.assert_called_once_with(
        name='Test',
        appliance_type=ApplianceType.FRIDGE,
        low_c=1,
        high_c=2,
        alert_threshold_s=3
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []
    
