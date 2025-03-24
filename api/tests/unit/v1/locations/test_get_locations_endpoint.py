from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4

import pytest

from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import get_api_key_access_scopes_helper, get_api_key_data, get_locations_service, get_access_token_data, get_user_access_grants_helper
from app.v1.organizations.schemas.organization import Organization
from app.v1.schemas import AccessScope
from app.v1.locations.schemas.location import Location


test_client = TestClient(app)


def test_get_locations_is_unauthorized_without_token_or_api_key():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/locations?organization_id={uuid4()}')
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
def test_get_locations_access_scope_responses_for_jwt_auth(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    locations_service_mock: Mock,
    location: Location,
    organization: Organization
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    locations_service_mock.filter_by.return_value = [location]
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/locations?organization_id={organization.organization_id}')

    assert response.status_code == response_code


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.LOCATIONS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.LOCATIONS_READ], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_get_locations_access_scope_responses_for_api_key_auth(
    access_scopes: List[AccessScope],
    response_code: int,
    locations_service_mock: Mock,
    location: Location,
    organization: Organization,
    api_key: APIKey,
    api_key_access_scopes_helper_mock: Mock
):
    app.dependency_overrides[get_api_key_data] = lambda: api_key

    api_key_access_scopes_helper_mock.get_all_access_scopes_for_api_key.return_value = access_scopes
    app.dependency_overrides[get_api_key_access_scopes_helper] = lambda: api_key_access_scopes_helper_mock

    locations_service_mock.filter_by.return_value = [location]
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/locations?organization_id={organization.organization_id}')

    assert response.status_code == response_code


def test_get_locations_success_response_when_jwt_auth(
    token_data_with_access_scopes: Callable,
    locations_service_mock: Mock,
    location: Location,
    organization: Organization
):
    token_data = token_data_with_access_scopes([AccessScope.LOCATIONS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    locations_service_mock.filter_by.return_value = [location]
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/locations?organization_id={organization.organization_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
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
    ]


def test_get_locations_success_response_when_api_key_auth(
    locations_service_mock: Mock,
    location: Location,
    organization: Organization,
    api_key: APIKey,
    api_key_access_scopes_helper_mock: Mock
):
    app.dependency_overrides[get_api_key_data] = lambda: api_key

    api_key_access_scopes_helper_mock.get_all_access_scopes_for_api_key.return_value = [AccessScope.LOCATIONS_READ]
    app.dependency_overrides[get_api_key_access_scopes_helper] = lambda: api_key_access_scopes_helper_mock

    locations_service_mock.filter_by.return_value = [location]
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/locations?organization_id={organization.organization_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
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
    ]


def test_get_locations_when_no_locations_exist_for_organization(
    token_data_with_access_scopes: Callable,
    locations_service_mock: Mock,
    organization: Organization
):
    token_data = token_data_with_access_scopes([AccessScope.LOCATIONS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    locations_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/locations?organization_id={organization.organization_id}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


def test_get_locations_when_organization_is_unauthorized(
    token_data_with_access_scopes: Callable,
    locations_service_mock: Mock,
    user_access_grants_helper_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.LOCATIONS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data
    user_access_grants_helper_mock.is_user_authorized_for_organization_read.return_value = False
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    locations_service_mock.filter_by.return_value = []
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/locations?organization_id={uuid4()}')

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_locations_by_name_success_response(
    token_data_with_access_scopes: Callable,
    locations_service_mock: Mock,
    location: Location
):
    token_data = token_data_with_access_scopes([AccessScope.LOCATIONS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    locations_service_mock.filter_by.return_value = [location, ]
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/locations?name={location.name}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
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
    ]


def test_get_locations_filters_unauthorized_locations_when_using_jwt_auth(
    token_data_with_access_scopes: Callable,
    locations_service_mock: Mock,
    location: Location,
    user_access_grants_helper_mock: Mock
):
    token_data = token_data_with_access_scopes([AccessScope.LOCATIONS_READ])
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    user_access_grants_helper_mock.is_user_authorized_for_location_read.side_effect = [True, False]
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    locations_service_mock.filter_by.return_value = [
        location,
        Location(
            name='Unauthorized Location',
            address='123 Main St',
            city='Springfield',
            state='IL',
            zip_code='62701',
            country='USA',
            latitude=39.799372,
            longitude=-89.644902,
            timezone='America/Chicago',
            organization_id=uuid4(),
            location_id=uuid4(),
            created_at=location.created_at,
            updated_at=location.updated_at
        )
    ]
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.get(f'/v1/locations?name={location.name}')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
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
    ]