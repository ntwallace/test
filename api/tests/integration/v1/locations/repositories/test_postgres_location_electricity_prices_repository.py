from datetime import datetime
from uuid import uuid4
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.errors import NotFoundError
from app.v1.locations.models.location_electricity_price import LocationElectricityPrice as LocationElectricityPriceModel
from app.v1.locations.repositories.locations_repository import PostgresLocationsRepository
from app.v1.locations.repositories.location_electricity_prices_repository import PostgresLocationElectricityPricesRepository
from app.v1.locations.schemas.location import LocationCreate
from app.v1.locations.schemas.location_electricity_price import LocationElectricityPrice, LocationElectricityPriceCreate, LocationElectricityPriceUpdate


def test_create_inserts_location_electricity_price(db_session_for_tests: Session):
    locations_repository = PostgresLocationsRepository(db_session_for_tests)
    location_electricity_prices_repository = PostgresLocationElectricityPricesRepository(db_session_for_tests)

    location = locations_repository.create(LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Test City',
        state='TS',
        zip_code='12345',
        country='Test Country',
        timezone='Test Timezone',
        latitude=0.0,
        longitude=0.0,
        organization_id=uuid4()
    ))

    location_electricity_price = location_electricity_prices_repository.create_location_electricity_price(LocationElectricityPriceCreate(
        location_id=location.location_id,
        comment='Test Comment',
        price_per_kwh=0.123,
        started_at=datetime(2021, 1, 1, 0, 0, 0),
        ended_at=datetime(2021, 1, 1, 0, 0, 0)
    ))

    location_electricity_price_models = db_session_for_tests.query(LocationElectricityPriceModel).all()
    assert len(location_electricity_price_models) == 1
    location_electricity_price_model = location_electricity_price_models[0]
    assert location_electricity_price_model.location_electricity_price_id == location_electricity_price.location_electricity_price_id
    assert location_electricity_price_model.location_id == location_electricity_price.location_id
    assert location_electricity_price_model.comment == location_electricity_price.comment
    assert location_electricity_price_model.price_per_kwh == location_electricity_price.price_per_kwh
    assert location_electricity_price_model.started_at == location_electricity_price.started_at
    assert location_electricity_price_model.ended_at == location_electricity_price.ended_at
    assert location_electricity_price_model.created_at == location_electricity_price.created_at
    assert location_electricity_price_model.updated_at == location_electricity_price.updated_at


def test_create_raises_error_when_creating_location_electricity_price_with_noexistent_location(db_session_for_tests: Session):
    location_electricity_prices_repository = PostgresLocationElectricityPricesRepository(db_session_for_tests)

    with pytest.raises(IntegrityError):
        location_electricity_prices_repository.create_location_electricity_price(LocationElectricityPriceCreate(
            location_id=uuid4(),
            comment='Test Comment',
            price_per_kwh=0.123,
            started_at=datetime(2021, 1, 1, 0, 0, 0),
            ended_at=datetime(2021, 1, 1, 0, 0, 0)
        ))


def test_update_location_electricity_price_when_resource_exists(db_session_for_tests: Session):
    locations_repository = PostgresLocationsRepository(db_session_for_tests)
    location_electricity_prices_repository = PostgresLocationElectricityPricesRepository(db_session_for_tests)

    location = locations_repository.create(LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Test City',
        state='TS',
        zip_code='12345',
        country='Test Country',
        timezone='Test Timezone',
        latitude=0.0,
        longitude=0.0,
        organization_id=uuid4()
    ))

    location_electricity_price = location_electricity_prices_repository.create_location_electricity_price(LocationElectricityPriceCreate(
        location_id=location.location_id,
        comment='Test Comment',
        price_per_kwh=0.123,
        started_at=datetime(2021, 1, 1, 0, 0, 0),
        ended_at=datetime(2021, 1, 1, 0, 0, 0)
    ))

    updated_location_electricity_price = location_electricity_prices_repository.update_location_electricity_price(LocationElectricityPriceUpdate(
        location_electricity_price_id=location_electricity_price.location_electricity_price_id,
        ended_at=datetime(2021, 1, 2, 0, 0, 0)
    ))

    location_electricity_price_models = db_session_for_tests.query(LocationElectricityPriceModel).all()
    assert len(location_electricity_price_models) == 1
    location_electricity_price_model = location_electricity_price_models[0]
    assert location_electricity_price_model.location_electricity_price_id == updated_location_electricity_price.location_electricity_price_id
    assert location_electricity_price_model.location_id == updated_location_electricity_price.location_id
    assert location_electricity_price_model.comment == updated_location_electricity_price.comment
    assert location_electricity_price_model.price_per_kwh == updated_location_electricity_price.price_per_kwh
    assert location_electricity_price_model.started_at == updated_location_electricity_price.started_at
    assert location_electricity_price_model.ended_at == updated_location_electricity_price.ended_at
    assert location_electricity_price_model.created_at == updated_location_electricity_price.created_at
    assert location_electricity_price_model.updated_at == updated_location_electricity_price.updated_at


def test_update_raises_error_when_location_electricity_price_does_not_exist(db_session_for_tests: Session):
    location_electricity_prices_repository = PostgresLocationElectricityPricesRepository(db_session_for_tests)

    with pytest.raises(NotFoundError):
        location_electricity_prices_repository.update_location_electricity_price(LocationElectricityPriceUpdate(
            location_electricity_price_id=uuid4(),
            ended_at=datetime(2021, 1, 2, 0, 0, 0)
        ))


def test_get_current_location_electricity_price_returns_most_recent_resource(mocker, db_session_for_tests: Session):
    mock_datetime = mocker.patch("app.v1.locations.repositories.location_electricity_prices_repository.datetime")
    mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)

    locations_repository = PostgresLocationsRepository(db_session_for_tests)
    location_electricity_prices_repository = PostgresLocationElectricityPricesRepository(db_session_for_tests)

    location = locations_repository.create(LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Test City',
        state='TS',
        zip_code='12345',
        country='Test Country',
        timezone='Test Timezone',
        latitude=0.0,
        longitude=0.0,
        organization_id=uuid4()
    ))

    location_electricity_prices_repository.create_location_electricity_price(LocationElectricityPriceCreate(
        location_id=location.location_id,
        comment='Test Comment 1',
        price_per_kwh=0.124,
        started_at=datetime(2023, 12, 1, 0, 0, 0),
        ended_at=datetime(2023, 12, 31, 23, 59, 59)
    ))
    most_recent_location_electricity_price = location_electricity_prices_repository.create_location_electricity_price(LocationElectricityPriceCreate(
        location_id=location.location_id,
        comment='Test Comment 2',
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 1, 0, 0, 0),
        ended_at=None
    ))
    
    current_location_electricity_price = location_electricity_prices_repository.get_current_location_electricity_price(location.location_id)

    assert current_location_electricity_price is not None
    assert current_location_electricity_price.location_id == location.location_id
    assert current_location_electricity_price.comment == most_recent_location_electricity_price.comment


def test_get_current_location_electricity_price_exludes_resources_with_ended_at_before_current_datetime(mocker, db_session_for_tests: Session):
    mock_datetime = mocker.patch("app.v1.locations.repositories.location_electricity_prices_repository.datetime")
    mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)

    locations_repository = PostgresLocationsRepository(db_session_for_tests)
    location_electricity_prices_repository = PostgresLocationElectricityPricesRepository(db_session_for_tests)

    location = locations_repository.create(LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Test City',
        state='TS',
        zip_code='12345',
        country='Test Country',
        timezone='Test Timezone',
        latitude=0.0,
        longitude=0.0,
        organization_id=uuid4()
    ))

    location_electricity_prices_repository.create_location_electricity_price(LocationElectricityPriceCreate(
        location_id=location.location_id,
        comment='Test Comment 1',
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 1, 0, 0, 0),
        ended_at=datetime(2024, 1, 1, 0, 0, 0)
    ))
    most_recent_resource = location_electricity_prices_repository.create_location_electricity_price(LocationElectricityPriceCreate(
        location_id=location.location_id,
        comment='Test Comment 2',
        price_per_kwh=0.124,
        started_at=datetime(2024, 1, 2, 0, 0, 0),
        ended_at=datetime(2024, 1, 2, 0, 0, 0)
    ))

    current_location_electricity_price = location_electricity_prices_repository.get_current_location_electricity_price(location.location_id)

    assert current_location_electricity_price is not None
    assert current_location_electricity_price.location_electricity_price_id == most_recent_resource.location_electricity_price_id


def test_get_location_electricity_prices_response(db_session_for_tests: Session):
    locations_repository = PostgresLocationsRepository(db_session_for_tests)
    location_electricity_prices_repository = PostgresLocationElectricityPricesRepository(db_session_for_tests)

    location = locations_repository.create(LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Test City',
        state='TS',
        zip_code='12345',
        country='Test Country',
        timezone='Test Timezone',
        latitude=0.0,
        longitude=0.0,
        organization_id=uuid4()
    ))

    location_electricity_prices_repository.create_location_electricity_price(LocationElectricityPriceCreate(
        location_id=location.location_id,
        comment='Test Comment 1',
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 1, 0, 0, 0),
        ended_at=datetime(2024, 1, 1, 0, 0, 0)
    ))
    location_electricity_price_1 = location_electricity_prices_repository.create_location_electricity_price(LocationElectricityPriceCreate(
        location_id=location.location_id,
        comment='Test Comment 2',
        price_per_kwh=0.124,
        started_at=datetime(2024, 1, 2, 0, 0, 0),
        ended_at=datetime(2024, 1, 2, 0, 0, 0)
    ))
    location_electricity_price_2 = location_electricity_prices_repository.create_location_electricity_price(LocationElectricityPriceCreate(
        location_id=location.location_id,
        comment='Test Comment 3',
        price_per_kwh=0.125,
        started_at=datetime(2024, 1, 3, 0, 0, 0),
        ended_at=None
    ))

    location_electricity_prices = location_electricity_prices_repository.get_location_electricity_prices(location.location_id, datetime(2024, 1, 1))

    assert len(location_electricity_prices) == 2
    assert location_electricity_price_1 in location_electricity_prices
    assert location_electricity_price_2 in location_electricity_prices