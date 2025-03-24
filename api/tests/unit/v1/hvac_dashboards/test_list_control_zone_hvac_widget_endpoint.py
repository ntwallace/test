from datetime import datetime
from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import get_access_token_data, get_api_key_access_scopes_helper, get_api_key_data, get_control_zone_hvac_widgets_service, get_hvac_zones_service, get_locations_service, get_hvac_dashboards_service, get_user_access_grants_helper
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import ControlZoneHvacWidget


test_client = TestClient(app)


def test_list_control_zone_hvac_widgets_is_unauthorized_without_token():
    response = test_client.get('/v1/control-zone-hvac-widgets')
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
def test_list_control_zone_hvac_widgets_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    control_zone_hvac_widgets_service_mock: Mock,
    hvac_zones_service_mock: Mock,
    locations_service_mock: Mock,
    hvac_dashboards_service_mock: Mock
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock
    app.dependency_overrides[get_hvac_dashboards_service] = lambda: hvac_dashboards_service_mock
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock
    app.dependency_overrides[get_control_zone_hvac_widgets_service] = lambda: control_zone_hvac_widgets_service_mock

    response = test_client.get('/v1/control-zone-hvac-widgets')

    assert response.status_code == response_code


def test_list_control_zone_hvac_widgets_success_response(
    control_zone_hvac_widget: ControlZoneHvacWidget,
    token_data_with_access_scopes: Callable,
    control_zone_hvac_widgets_service_mock: Mock,
    hvac_zones_service_mock: Mock,
    locations_service_mock: Mock,
    hvac_dashboards_service_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    control_zone_hvac_widgets_service_mock.filter_by.return_value = [control_zone_hvac_widget, ]
    app.dependency_overrides[get_control_zone_hvac_widgets_service] = lambda: control_zone_hvac_widgets_service_mock
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock
    app.dependency_overrides[get_hvac_dashboards_service] = lambda: hvac_dashboards_service_mock

    response = test_client.get('/v1/control-zone-hvac-widgets')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'hvac_widget_id': str(control_zone_hvac_widget.hvac_widget_id),
        'name': control_zone_hvac_widget.name,
        'hvac_dashboard_id': str(control_zone_hvac_widget.hvac_dashboard_id),
        'hvac_zone_id': str(control_zone_hvac_widget.hvac_zone_id),
        'created_at': control_zone_hvac_widget.created_at.isoformat(),
        'updated_at': control_zone_hvac_widget.updated_at.isoformat(),
        'monday_schedule': None,
        'tuesday_schedule': None,
        'wednesday_schedule': None,
        'thursday_schedule': None,
        'friday_schedule': None,
        'saturday_schedule': None,
        'sunday_schedule': None,
        'temperature_place_links': []
    }]


def test_list_control_zone_hvac_widgets_empty_response(
    admin_all_access_token_data: Callable,
    control_zone_hvac_widgets_service_mock: Mock,
    hvac_zones_service_mock: Mock,
    locations_service_mock: Mock,
    hvac_dashboards_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    control_zone_hvac_widgets_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_control_zone_hvac_widgets_service] = lambda: control_zone_hvac_widgets_service_mock
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock
    app.dependency_overrides[get_hvac_dashboards_service] = lambda: hvac_dashboards_service_mock

    response = test_client.get('/v1/control-zone-hvac-widgets')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_list_control_zone_hvac_widgets_returns_only_authorized_resources(
    control_zone_hvac_widget: ControlZoneHvacWidget,
    token_data_with_access_scopes: Callable,
    control_zone_hvac_widgets_service_mock: Mock,
    hvac_zones_service_mock: Mock,
    locations_service_mock: Mock,
    hvac_dashboards_service_mock: Mock,
    user_access_grants_helper_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.ADMIN, AccessScope.HVAC_DASHBOARDS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    user_access_grants_helper_mock.is_user_authorized_for_location_read.side_effect = [True, False]
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock


    control_zone_hvac_widgets_service_mock.filter_by.return_value = [
        control_zone_hvac_widget,
        ControlZoneHvacWidget(
            hvac_widget_id=uuid4(),
            name='Test Control Zone HVAC Widget 2',
            hvac_dashboard_id=uuid4(),
            hvac_zone_id=uuid4(),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )]
    app.dependency_overrides[get_control_zone_hvac_widgets_service] = lambda: control_zone_hvac_widgets_service_mock
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock
    app.dependency_overrides[get_hvac_dashboards_service] = lambda: hvac_dashboards_service_mock
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get('/v1/control-zone-hvac-widgets')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'hvac_widget_id': str(control_zone_hvac_widget.hvac_widget_id),
        'name': control_zone_hvac_widget.name,
        'hvac_dashboard_id': str(control_zone_hvac_widget.hvac_dashboard_id),
        'hvac_zone_id': str(control_zone_hvac_widget.hvac_zone_id),
        'created_at': control_zone_hvac_widget.created_at.isoformat(),
        'updated_at': control_zone_hvac_widget.updated_at.isoformat(),
        'monday_schedule': None,
        'tuesday_schedule': None,
        'wednesday_schedule': None,
        'thursday_schedule': None,
        'friday_schedule': None,
        'saturday_schedule': None,
        'sunday_schedule': None,
        'temperature_place_links': []
    }]
