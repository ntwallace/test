from typing import Callable, List
from unittest.mock import Mock

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_electric_panels_service, get_access_token_data
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanel
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_create_electric_panel_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post('/v1/electric-panels')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.ELECTRICITY_MONITORING_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ELECTRICITY_MONITORING_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ELECTRICITY_MONITORING_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_electric_panel_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel,
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    electric_panels_service_mock.create_electric_panel.return_value = electric_panel
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.post('/v1/electric-panels', json={
        "name": "Test Electric Panel",
        "panel_type": "mdp",
        "location_id": str(electric_panel.location_id),
        "breaker_count": 1,
        "electric_panel_id": str(electric_panel.electric_panel_id)
    })

    assert response.status_code == response_code


def test_create_electric_panel_success_response(
    admin_all_access_token_data: AccessTokenData,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    electric_panels_service_mock.create_electric_panel.return_value = electric_panel
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock


    response = test_client.post('/v1/electric-panels', json={
        "name": electric_panel.name,
        "panel_type": electric_panel.panel_type.value,
        "location_id": str(electric_panel.location_id),
        "breaker_count": electric_panel.breaker_count,
        "electric_panel_id": str(electric_panel.electric_panel_id)
    })

    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json['electric_panel_id'] == str(electric_panel.electric_panel_id)
    assert response_json['name'] == electric_panel.name
    assert response_json['panel_type'] == electric_panel.panel_type.value
    assert response_json['location_id'] == str(electric_panel.location_id)
    assert response_json['breaker_count'] == electric_panel.breaker_count
    

def test_create_electric_panel_when_electric_panel_exists(
    admin_all_access_token_data: AccessTokenData,
    electric_panels_service_mock: Mock,
    electric_panel: ElectricPanel,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    electric_panels_service_mock.create_electric_panel.side_effect = ValueError
    app.dependency_overrides[get_electric_panels_service] = lambda: electric_panels_service_mock

    response = test_client.post('/v1/electric-panels', json={
        "name": "Test Electric Panel",
        "panel_type": "mdp",
        "location_id": str(electric_panel.location_id),
        "breaker_count": 1,
        "electric_panel_id": str(electric_panel.electric_panel_id)
    })

    assert response.status_code == 400
