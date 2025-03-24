from typing import Callable, List, Optional
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import get_api_key_access_scopes_helper, get_api_key_data, get_hvac_zones_service, get_locations_service, get_access_token_data
from app.v1.locations.schemas.location import Location
from app.v1.hvac.schemas.hvac_zone import HvacZone
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_get_hvac_zones_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/hvac-zones?location_id={uuid4()}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.HVAC_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.HVAC_READ], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_get_hvac_zones_access_scopes(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    hvac_zones_service_mock: Mock,
    hvac_zone: HvacZone,
    location: Location,
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    hvac_zones_service_mock.filter_by.return_value = [hvac_zone,]
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock

    response = test_client.get(f'/v1/hvac-zones?location_id={location.location_id}')

    assert response.status_code == response_code


def test_get_hvac_zones_success_response(
    admin_all_access_token_data: AccessTokenData,
    hvac_zones_service_mock: Mock,
    hvac_zone: HvacZone,
    location: Location,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    hvac_zones_service_mock.filter_by.return_value = [hvac_zone,]
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock

    locations_service_mock.get_location.return_value = location
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/hvac-zones?location_id={location.location_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'name': hvac_zone.name,
        'hvac_zone_id': str(hvac_zone.hvac_zone_id),
        'location_id': str(hvac_zone.location_id),
        'created_at': hvac_zone.created_at.isoformat(),
        'updated_at': hvac_zone.updated_at.isoformat()
    }]


def test_list_hvac_zones_sucess_when_api_key_auth(
    api_key: APIKey,
    hvac_zone: HvacZone,
    location: Location,
    api_key_access_scopes_helper_mock: Mock,
    hvac_zones_service_mock: Mock,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_api_key_data] = lambda: api_key

    api_key_access_scopes_helper_mock.get_all_access_scopes_for_api_key.return_value = [AccessScope.HVAC_READ]
    app.dependency_overrides[get_api_key_access_scopes_helper] = lambda: api_key_access_scopes_helper_mock

    hvac_zones_service_mock.filter_by.return_value = [hvac_zone,]
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock

    locations_service_mock.get_location.return_value = location
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/hvac-zones?location_id={location.location_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'name': hvac_zone.name,
        'hvac_zone_id': str(hvac_zone.hvac_zone_id),
        'location_id': str(hvac_zone.location_id),
        'created_at': hvac_zone.created_at.isoformat(),
        'updated_at': hvac_zone.updated_at.isoformat()
    }]


def test_get_hvac_zones_when_hvac_zones_dont_exist(
    admin_all_access_token_data: AccessTokenData,
    hvac_zones_service_mock: Mock,
    location: Location,
    locations_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    hvac_zones_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock

    locations_service_mock.get_location.return_value = location
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/hvac-zones?location_id={location.location_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_hvac_zone_when_location_is_unauthorized(
    no_access_token_data: AccessTokenData,
    hvac_zones_service_mock: Mock,
    hvac_zone: HvacZone
):
    app.dependency_overrides[get_access_token_data] = lambda: no_access_token_data

    hvac_zone.location_id = uuid4()
    hvac_zones_service_mock.filter_by.return_value = [hvac_zone,]
    app.dependency_overrides[get_hvac_zones_service] = lambda: hvac_zones_service_mock

    response = test_client.get(f'/v1/hvac-zones?location_id={uuid4()}')

    assert response.status_code == status.HTTP_403_FORBIDDEN
