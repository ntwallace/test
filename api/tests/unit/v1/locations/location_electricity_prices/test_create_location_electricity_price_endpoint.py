from typing import Callable, List
from unittest.mock import Mock
from uuid import uuid4
from fastapi import status
from fastapi.testclient import TestClient
import pytest

from app.main import app
from app.v1.dependencies import get_access_token_data, get_location_electricity_prices_service
from app.v1.locations.schemas.location import Location
from app.v1.locations.schemas.location_electricity_price import LocationElectricityPrice
from app.v1.organizations.schemas.organization import Organization
from app.v1.schemas import AccessScope, AccessTokenData


test_client = TestClient(app)


def test_create_location_is_unauthorized_without_token():
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    response = test_client.post(f'/v1/locations/{uuid4()}/electricity-prices')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ('access_scopes', 'response_code'),
    [
        ([AccessScope.LOCATION_ELECTRICITY_PRICES_WRITE], status.HTTP_201_CREATED),
        ([AccessScope.LOCATION_ELECTRICITY_PRICES_READ], status.HTTP_403_FORBIDDEN),
        ([AccessScope.ADMIN], status.HTTP_403_FORBIDDEN),
        ([AccessScope.LOCATIONS_WRITE], status.HTTP_403_FORBIDDEN),
        ([AccessScope.LOCATIONS_READ], status.HTTP_403_FORBIDDEN),
        ([], status.HTTP_403_FORBIDDEN),
    ]
)
def test_create_location_electricy_price_access_scope_responses(
    access_scopes: List[AccessScope],
    response_code: int,
    token_data_with_access_scopes: Callable,
    location: Location,
    location_electricity_prices_service_mock: Mock,
    location_electricity_price: LocationElectricityPrice,
):
    token_data = token_data_with_access_scopes(access_scopes)
    app.dependency_overrides[get_access_token_data] = lambda: token_data

    location_electricity_prices_service_mock.create_location_electricity_price.return_value = location_electricity_price
    app.dependency_overrides[get_location_electricity_prices_service] = lambda: location_electricity_prices_service_mock

    response = test_client.post(
        f'/v1/locations/{location.location_id}/electricity-prices',
        json={
            'location_id': str(location.location_id),
            'comment': 'Initial price',
            'price_per_kwh': 0.123,
            'started_at': '2021-01-01T00:00:00Z'
        }
    )

    assert response.status_code == response_code


def test_create_location_electricity_price_success_response(
    admin_all_access_token_data: AccessTokenData,
    location_electricity_prices_service_mock: Mock,
    location: Location,
    location_electricity_price: LocationElectricityPrice,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    location_electricity_prices_service_mock.create_location_electricity_price.return_value = location_electricity_price
    app.dependency_overrides[get_location_electricity_prices_service] = lambda: location_electricity_prices_service_mock

    response = test_client.post(
        f'/v1/locations/{location.location_id}/electricity-prices',
        json={
            'location_id': str(location.location_id),
            'comment': 'Initial price',
            'price_per_kwh': 0.123,
            'started_at': '2024-01-01T00:00:00'
        }
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'location_id': str(location.location_id),
        'comment': 'Initial price',
        'price_per_kwh': 0.123,
        'started_at': '2024-01-01T00:00:00',
        'ended_at': None,
        'location_electricity_price_id': str(location_electricity_price.location_electricity_price_id),
        'created_at': location_electricity_price.created_at.isoformat(),
        'updated_at': location_electricity_price.updated_at.isoformat()
    }


def test_create_location_electricity_price_with_invalid_location_id(
    admin_all_access_token_data: AccessTokenData,
    location: Location,
    location_electricity_prices_service_mock: Mock,
    location_electricity_price: LocationElectricityPrice,
):
    app.dependency_overrides[get_access_token_data] = lambda: admin_all_access_token_data

    location_electricity_prices_service_mock.create_location_electricity_price.return_value = location_electricity_price
    app.dependency_overrides[get_location_electricity_prices_service] = lambda: location_electricity_prices_service_mock

    response = test_client.post(
        f'/v1/locations/{location.location_id}/electricity-prices',
        json={
            'location_id': str(uuid4()),
            'comment': 'Initial price',
            'price_per_kwh': 0.123,
            'started_at': '2021-01-01T00:00:00Z'
        }
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
