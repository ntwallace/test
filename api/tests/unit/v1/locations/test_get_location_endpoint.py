from datetime import datetime
from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.dependencies import get_locations_service, get_access_token_data, get_user_access_grants_helper
from app.v1.locations.schemas.location import Location
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_get_location_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/locations/{uuid4()}')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.LOCATIONS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.LOCATIONS_READ], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_get_location_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    locations_service_mock: Mock,
    location: Location
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    locations_service_mock.get_location.return_value = location
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/locations/{location.location_id}')

    assert response.status_code == response_code


def test_get_location_success_response(
    token_data_with_access_scopes: Callable,
    locations_service_mock: Mock,
    location: Location,
):
    token_data = token_data_with_access_scopes([AccessScope.LOCATIONS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    locations_service_mock.get_location.return_value = location
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/locations/{location.location_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'location_id': str(location.location_id),
        'name': location.name,
        'address': location.address,
        'city': location.city,
        'state': location.state,
        'zip_code': location.zip_code,
        'country': location.country,
        'latitude': location.latitude,
        'longitude': location.longitude,
        'timezone': location.timezone,
        'organization_id': str(location.organization_id),
        'created_at': location.created_at.isoformat(),
        'updated_at': location.updated_at.isoformat()
    }


def test_get_location_when_location_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    locations_service_mock: Mock,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    locations_service_mock.get_location.return_value = None
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/locations/{uuid4()}')

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_location_when_organization_is_unauthorized(
    token_data_with_access_scopes: Callable,
    locations_service_mock: Mock,
    user_access_grants_helper_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.LOCATIONS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    user_access_grants_helper_mock.is_user_authorized_for_location_read.return_value = False
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    unauthorized_location = Location(
        location_id=uuid4(),
        name='Unauthorized Location',
        address='1234 Power St',
        city='Milwaukee',
        state='WI',
        zip_code='53212',
        country='USA',
        latitude=1.0,
        longitude=2.0,
        timezone='America/Chicago',
        organization_id=uuid4(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    locations_service_mock.get_location.return_value = unauthorized_location
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/locations/{unauthorized_location.location_id}')

    assert response.status_code == status.HTTP_403_FORBIDDEN
