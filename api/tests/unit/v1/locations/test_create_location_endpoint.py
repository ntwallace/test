from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.main import app
from app.v1.dependencies import get_location_operating_hours_service, get_locations_service, get_locations_service, get_access_token_data
from app.v1.organizations.schemas.organization import Organization
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.locations.schemas.location import Location


test_client = TestClient(app)


def test_create_location_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post('/v1/locations')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN, AccessScope.LOCATIONS_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.LOCATIONS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.LOCATIONS_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_location_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    locations_service_mock: Mock,
    location_operating_hours_service_mock: Mock,
    location: Location,
    organization: Organization
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    app.dependency_overrides[get_location_operating_hours_service] = lambda: location_operating_hours_service_mock

    locations_service_mock.create_location.return_value = location
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.post(
        '/v1/locations', 
        json={
            'name': 'Test Location',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'country': 'USA',
            'latitude': 0.0,
            'longitude': 0.0,
            'timezone': 'America/Chicago',
            'organization_id': str(organization.organization_id)
        }
    )

    assert response.status_code == response_code


def test_create_location_success_response(
    admin_all_access_token_data: AccessTokenData,
    locations_service_mock: Mock,
    location_operating_hours_service_mock: Mock,
    location: Location,
    organization: Organization
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    app.dependency_overrides[get_location_operating_hours_service] = lambda: location_operating_hours_service_mock

    locations_service_mock.create_location.return_value = location
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.post(
        '/v1/locations', 
        json={
            'name': 'Test Location',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'country': 'USA',
            'latitude': 0.0,
            'longitude': 0.0,
            'timezone': 'America/Chicago',
            'organization_id': str(organization.organization_id)
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
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


def test_create_location_when_location_exists(
    admin_all_access_token_data: AccessTokenData,
    locations_service_mock: Mock,
    location: Location,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data
    locations_service_mock.create_location.side_effect = IntegrityError('mock', 'mock', 'mock')
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock

    response = test_client.post(
        '/v1/locations', 
        json={
            'name': location.name,
            'address': location.address,
            'city': location.city,
            'state': location.state,
            'zip_code': location.zip_code,
            'country': location.country,
            'latitude': location.latitude,
            'longitude': location.longitude,
            'timezone': location.timezone,
            'organization_id': str(location.organization_id)
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_create_location_when_organization_is_unauthorized(
    token_data_with_access_scopes: Callable,
):
    token_data = token_data_with_access_scopes([AccessScope.LOCATIONS_WRITE])
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    response = test_client.post(
        '/v1/locations', 
        json={
            'name': 'Test Location',
            'address': '123 Test St',
            'city': 'Test City',
            'state': 'TS',
            'zip_code': '12345',
            'country': 'USA',
            'latitude': 0.0,
            'longitude': 0.0,
            'timezone': 'America/Chicago',
            'organization_id': str(uuid4())
        }
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
