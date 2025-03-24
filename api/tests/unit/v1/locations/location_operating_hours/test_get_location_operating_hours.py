from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient


from app.main import app
from app.v1.dependencies import get_location_operating_hours_service, get_access_token_data, get_user_access_grants_helper
from app.v1.locations.schemas.location import Location
from app.v1.locations.schemas.location_operating_hours import LocationOperatingHours, LocationOperatingHoursMap
from app.v1.schemas import AccessScope, AccessTokenData

test_client = TestClient(app)


def test_get_location_operating_hours_when_missing_auth_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.get(f'/v1/locations/{uuid4()}/operating-hours')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.LOCATION_OPERATING_HOURS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.LOCATION_OPERATING_HOURS_READ], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN)
    ]
)
def test_get_location_operating_hours_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    location_operating_hours_service_mock: Mock,
    location: Location,
    location_operating_hours_list: List[LocationOperatingHours]
):
    print(location_operating_hours_list)
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    location_operating_hours_service_mock.get_location_operating_hours_for_location.return_value = location_operating_hours_list
    app.dependency_overrides[get_location_operating_hours_service] = lambda: location_operating_hours_service_mock

    response = test_client.get(f'/v1/locations/{location.location_id}/operating-hours')
    assert response.status_code == response_code


def test_get_location_operating_hours_success_response(
    admin_all_access_token_data: AccessTokenData,
    location_operating_hours_service_mock: Mock,
    location: Location,
    location_operating_hours_list: List[LocationOperatingHours]
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    location_operating_hours_service_mock.get_location_operating_hours_for_location.return_value = location_operating_hours_list
    app.dependency_overrides[get_location_operating_hours_service] = lambda: location_operating_hours_service_mock

    response = test_client.get(f'/v1/locations/{location.location_id}/operating-hours')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        location_operating_hours.day_of_week: {
            'location_id': str(location_operating_hours.location_id),
            'day_of_week': location_operating_hours.day_of_week,
            'is_open': location_operating_hours.is_open,
            'work_start_time': location_operating_hours.work_start_time.isoformat(),
            'open_time': location_operating_hours.open_time.isoformat(),
            'close_time': location_operating_hours.close_time.isoformat(),
            'work_end_time': location_operating_hours.work_end_time.isoformat(),
            'created_at': location_operating_hours.created_at.isoformat(),
            'updated_at': location_operating_hours.updated_at.isoformat()
        }
        for location_operating_hours in location_operating_hours_list
    }


def test_get_location_operating_hours_when_location_has_no_operating_hours(
    admin_all_access_token_data: AccessTokenData,
    location_operating_hours_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    location_operating_hours_service_mock.get_location_operating_hours_for_location.return_value = []
    app.dependency_overrides[get_location_operating_hours_service] = lambda: location_operating_hours_service_mock

    response = test_client.get(f'/v1/locations/{uuid4()}/operating-hours')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_location_operating_hours_when_location_is_unauthorized(
    read_access_token_data: AccessTokenData,
    location_operating_hours_service_mock: Mock,
    location_operating_hours: LocationOperatingHours,
    user_access_grants_helper_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: read_access_token_data
    user_access_grants_helper_mock.is_user_authorized_for_location_read.return_value = False
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock

    location_operating_hours_service_mock.get_location_operating_hours_for_location.return_value = location_operating_hours
    app.dependency_overrides[get_location_operating_hours_service] = lambda: location_operating_hours_service_mock

    response = test_client.get(f'/v1/locations/{location_operating_hours.location_id}/operating-hours')
    assert response.status_code == status.HTTP_403_FORBIDDEN
