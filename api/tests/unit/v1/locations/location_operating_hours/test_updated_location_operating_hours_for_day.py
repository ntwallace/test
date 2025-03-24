from datetime import datetime
from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4, UUID

import pytest

from fastapi import status
from fastapi.testclient import TestClient


from app.main import app
from app.v1.dependencies import get_location_operating_hours_service, get_access_token_data
from app.v1.locations.schemas.location_operating_hours import LocationOperatingHours
from app.v1.schemas import AccessScope, AccessTokenData

test_client = TestClient(app)


def test_update_location_operating_hours_for_day_when_missing_auth_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.put(f'/v1/locations/{uuid4()}/operating-hours/monday', json={
        'location_id': str(uuid4()),
        'day_of_week': 'monday',
        'is_open': True,
        'work_start_time': '01:00:00',
        'open_time': '02:00:00',
        'close_time': '03:00:00',
        'work_end_time': '04:00:00',
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.LOCATION_OPERATING_HOURS_WRITE], status.HTTP_200_OK),
        ([AccessScope.LOCATION_OPERATING_HOURS_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN)
    ]
)
def test_update_location_operating_hours_for_day_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    location_operating_hours_service_mock: Mock,
    location_operating_hours: LocationOperatingHours,
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    location_operating_hours_service_mock.get_location_operating_hours_for_location.return_value = [location_operating_hours, ]
    app.dependency_overrides[get_location_operating_hours_service] = lambda: location_operating_hours_service_mock

    response = test_client.put(f'/v1/locations/{location_operating_hours.location_id}/operating-hours/monday', json={
        'location_id': str(location_operating_hours.location_id),
        'day_of_week': 'monday',
        'is_open': True,
        'work_start_time': '01:00:00',
        'open_time': '02:00:00',
        'close_time': '03:00:00',
        'work_end_time': '04:00:00',
    })
    assert response.status_code == response_code


def test_update_location_operating_hours_for_day_success_response(
    admin_all_access_token_data: AccessTokenData,
    location_operating_hours_service_mock: Mock,
    location_operating_hours: LocationOperatingHours
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    updated_location_operating_hours = LocationOperatingHours(
        location_id=location_operating_hours.location_id,
        day_of_week='monday',
        is_open=True,
        work_start_time='01:00:00',
        open_time='02:00:00',
        close_time='03:00:00',
        work_end_time='04:00:00',
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    location_operating_hours_service_mock.update_location_operating_hours.return_value = updated_location_operating_hours
    app.dependency_overrides[get_location_operating_hours_service] = lambda: location_operating_hours_service_mock

    response = test_client.put(f'/v1/locations/{location_operating_hours.location_id}/operating-hours/monday', json={
        'location_id': str(updated_location_operating_hours.location_id),
        'day_of_week': updated_location_operating_hours.day_of_week,
        'is_open': updated_location_operating_hours.is_open,
        'work_start_time': updated_location_operating_hours.work_start_time.isoformat(),
        'open_time': updated_location_operating_hours.open_time.isoformat(),
        'close_time': updated_location_operating_hours.close_time.isoformat(),
        'work_end_time': updated_location_operating_hours.work_end_time.isoformat(),
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'location_id': str(updated_location_operating_hours.location_id),
        'day_of_week': updated_location_operating_hours.day_of_week,
        'is_open': updated_location_operating_hours.is_open,
        'work_start_time': updated_location_operating_hours.work_start_time.isoformat(),
        'open_time': updated_location_operating_hours.open_time.isoformat(),
        'close_time': updated_location_operating_hours.close_time.isoformat(),
        'work_end_time': updated_location_operating_hours.work_end_time.isoformat(),
        'created_at': updated_location_operating_hours.created_at.isoformat(),
        'updated_at': updated_location_operating_hours.updated_at.isoformat()
    }


def test_update_location_operating_hours_for_day_when_day_of_week_is_unknown(
    admin_all_access_token_data: AccessTokenData,
    location_operating_hours_service_mock: Mock,
    location_operating_hours: LocationOperatingHours
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    location_operating_hours_service_mock.update_location_operating_hours.return_value = location_operating_hours
    app.dependency_overrides[get_location_operating_hours_service] = lambda: location_operating_hours_service_mock

    response = test_client.put(f'/v1/locations/{location_operating_hours.location_id}/operating-hours/asdf', json={
        'location_id': str(location_operating_hours.location_id),
        'day_of_week': 'monday',
        'is_open': True,
        'work_start_time': '01:00:00',
        'open_time': '02:00:00',
        'close_time': '03:00:00',
        'work_end_time': '04:00:00',
    })
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_location_operating_hours_for_day_when_location_id_is_mismatched(
    admin_all_access_token_data: AccessTokenData,
    location_operating_hours_service_mock: Mock,
    location_operating_hours: LocationOperatingHours
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    location_operating_hours_service_mock.update_location_operating_hours.return_value = location_operating_hours
    app.dependency_overrides[get_location_operating_hours_service] = lambda: location_operating_hours_service_mock

    response = test_client.put(f'/v1/locations/{location_operating_hours.location_id}/operating-hours/monday', json={
        'location_id': str(uuid4()),
        'day_of_week': 'monday',
        'is_open': True,
        'work_start_time': '01:00:00',
        'open_time': '02:00:00',
        'close_time': '03:00:00',
        'work_end_time': '04:00:00',
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_location_operating_hours_when_day_of_week_is_mismatched(
    admin_all_access_token_data: AccessTokenData,
    location_operating_hours_service_mock: Mock,
    location_operating_hours: LocationOperatingHours
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    location_operating_hours_service_mock.update_location_operating_hours.return_value = location_operating_hours
    app.dependency_overrides[get_location_operating_hours_service] = lambda: location_operating_hours_service_mock

    response = test_client.put(f'/v1/locations/{location_operating_hours.location_id}/operating-hours/monday', json={
        'location_id': str(location_operating_hours.location_id),
        'day_of_week': 'tuesday',
        'is_open': True,
        'work_start_time': '01:00:00',
        'open_time': '02:00:00',
        'close_time': '03:00:00',
        'work_end_time': '04:00:00',
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_location_operating_hours_when_location_operating_hours_doesnt_exist(
    admin_all_access_token_data: AccessTokenData,
    location_operating_hours_service_mock: Mock
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    location_operating_hours_service_mock.update_location_operating_hours.side_effect = ValueError()
    app.dependency_overrides[get_location_operating_hours_service] = lambda: location_operating_hours_service_mock
    location_id = uuid4()
    response = test_client.put(f'/v1/locations/{location_id}/operating-hours/monday', json={
        'location_id': str(location_id),
        'day_of_week': 'monday',
        'is_open': True,
        'work_start_time': '01:00:00',
        'open_time': '02:00:00',
        'close_time': '03:00:00',
        'work_end_time': '04:00:00',
    })
    assert response.status_code == status.HTTP_404_NOT_FOUND