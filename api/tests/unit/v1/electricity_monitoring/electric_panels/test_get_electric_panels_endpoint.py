from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_electric_panels_service, get_access_token_data
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanel
from app.v1.locations.schemas.location import Location
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_get_electric_panels_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/electric-panels?location_id={uuid4()}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ELECTRICITY_MONITORING_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ELECTRICITY_MONITORING_READ], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_get_electric_panels_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel,
    location: Location
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    electric_panels_service_mock.filter_by.return_value = [electric_panel, ]
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.get(f'/v1/electric-panels?location_id={location.location_id}')
    
    assert response.status_code == response_code


def test_get_electric_panels_success_response(
    admin_all_access_token_data: AccessTokenData,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel,
    location: Location
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    electric_panels_service_mock.filter_by.return_value = [electric_panel, ]
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.get(f'/v1/electric-panels?location_id={location.location_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'name': electric_panel.name,
            'panel_type': electric_panel.panel_type.value,
            'location_id': str(electric_panel.location_id),
            'breaker_count': electric_panel.breaker_count,
            'electric_panel_id': str(electric_panel.electric_panel_id),
            'parent_electric_panel_id': str(electric_panel.parent_electric_panel_id) if electric_panel.parent_electric_panel_id is not None else None,
            'created_at': electric_panel.created_at.isoformat(),
            'updated_at': electric_panel.updated_at.isoformat()
        }
    ]


def test_get_electric_panels_when_no_electric_panels_exist(
    admin_all_access_token_data: AccessTokenData,
    electric_panels_service_mock: Mock,
    location: Location
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    electric_panels_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.get(f'/v1/electric-panels?location_id={location.location_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_electric_panels_when_location_is_unauthorized(
    no_access_token_data: AccessTokenData,
    electric_panels_service_mock: Mock,
):
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data
    electric_panels_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.get(f'/v1/electric-panels?location_id={uuid4()}')

    assert response.status_code == status.HTTP_403_FORBIDDEN
