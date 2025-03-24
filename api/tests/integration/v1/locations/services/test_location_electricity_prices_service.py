from datetime import datetime
from uuid import UUID, uuid4
import pytest
from sqlalchemy.orm import Session

from app.v1.locations.models.location_electricity_price import LocationElectricityPrice as LocationElectricityPriceModel
from app.v1.locations.repositories.location_electricity_prices_repository import PostgresLocationElectricityPricesRepository
from app.v1.locations.repositories.locations_repository import PostgresLocationsRepository
from app.v1.locations.schemas.location import Location, LocationCreate
from app.v1.locations.schemas.location_electricity_price import LocationElectricityPriceCreate, LocationElectricityPrice, LocationElectricityPriceUpdate
from app.v1.locations.services.location_electricity_prices import LocationElectricityPricesService
from app.v1.locations.services.locations import LocationsService

@pytest.fixture(scope="function")
def location_for_tests(db_session_for_tests: Session) -> Location:
    locations_service = LocationsService(PostgresLocationsRepository(db_session_for_tests))
    return locations_service.create_location(
        LocationCreate(
            name="Test location",
            address="123 Test St",
            city="Testville",
            state="TS",
            zip_code="12345",
            country="USA",
            timezone="America/New_York",
            latitude=0.0,
            longitude=0.0,
            organization_id=uuid4()
        )
    )

@pytest.fixture(scope="function")
def other_location_for_tests(db_session_for_tests: Session) -> Location:
    locations_service = LocationsService(PostgresLocationsRepository(db_session_for_tests))
    return locations_service.create_location(
        LocationCreate(
            name="Test location",
            address="123 Test St",
            city="Testville",
            state="TS",
            zip_code="12345",
            country="USA",
            timezone="America/New_York",
            latitude=0.0,
            longitude=0.0,
            organization_id=uuid4()
        )
    )

def test_create_location_electricity_price_creates_new_resource(db_session_for_tests: Session, location_for_tests: Location):
    """Test that the LocationElectricityPricesService.create_location_electricity_price method creates a new resource, if none exists."""
    location_electricity_prices_service = LocationElectricityPricesService(PostgresLocationElectricityPricesRepository(db_session_for_tests))
    location_electricity_price_create = LocationElectricityPriceCreate(
        location_id=location_for_tests.location_id,
        comment="Test location electricity price",
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 1)
    )

    location_electricity_price = location_electricity_prices_service.create_location_electricity_price(location_electricity_price_create)

    assert isinstance(location_electricity_price.location_electricity_price_id, UUID)
    assert location_electricity_price.location_id == location_electricity_price_create.location_id
    assert location_electricity_price.comment == location_electricity_price_create.comment
    assert location_electricity_price.price_per_kwh == location_electricity_price_create.price_per_kwh
    assert location_electricity_price.started_at == location_electricity_price_create.started_at
    assert location_electricity_price.ended_at is None

    location_electricity_price_from_db = db_session_for_tests.query(LocationElectricityPriceModel).get(location_electricity_price.location_electricity_price_id)
    assert location_electricity_price_from_db is not None
    assert LocationElectricityPrice.model_validate(location_electricity_price_from_db, from_attributes=True) == location_electricity_price


def test_create_location_electricity_price_updates_current_resources_ended_at_field(db_session_for_tests: Session, location_for_tests: Location):
    """Test that the LocationElectricityPricesService.create_location_electricity_price method updates the ended_at field of the current resource."""
    location_electricity_prices_service = LocationElectricityPricesService(PostgresLocationElectricityPricesRepository(db_session_for_tests))
    current_location_electricity_price = LocationElectricityPriceModel(
        location_id=location_for_tests.location_id,
        comment="Test location electricity price",
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 1)
    )
    db_session_for_tests.add(current_location_electricity_price)
    db_session_for_tests.commit()

    location_electricity_price_create = LocationElectricityPriceCreate(
        location_id=location_for_tests.location_id,
        comment="Test location electricity price",
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 2)
    )
    location_electricity_price = location_electricity_prices_service.create_location_electricity_price(location_electricity_price_create)

    assert isinstance(location_electricity_price.location_electricity_price_id, UUID)
    assert location_electricity_price.location_id == location_electricity_price_create.location_id
    assert location_electricity_price.comment == location_electricity_price_create.comment
    assert location_electricity_price.price_per_kwh == location_electricity_price_create.price_per_kwh
    assert location_electricity_price.started_at == location_electricity_price_create.started_at
    assert location_electricity_price.ended_at is None

    current_location_electricity_price_from_db = db_session_for_tests.query(LocationElectricityPriceModel).get(current_location_electricity_price.location_electricity_price_id)
    assert current_location_electricity_price_from_db is not None
    assert LocationElectricityPrice.model_validate(current_location_electricity_price_from_db, from_attributes=True).ended_at == location_electricity_price_create.started_at

    location_electricity_price_from_db = db_session_for_tests.query(LocationElectricityPriceModel).get(location_electricity_price.location_electricity_price_id)
    assert location_electricity_price_from_db is not None
    assert LocationElectricityPrice.model_validate(location_electricity_price_from_db, from_attributes=True) == location_electricity_price


def test_update_location_electricity_price_updates_resource_ended_at(db_session_for_tests: Session, location_for_tests: Location):
    """Test that the LocationElectricityPricesService.update_location_electricity_price method updates the ended_at field of the resource."""
    location_electricity_prices_service = LocationElectricityPricesService(PostgresLocationElectricityPricesRepository(db_session_for_tests))
    location_electricity_price = LocationElectricityPriceModel(
        location_id=location_for_tests.location_id,
        comment="Test location electricity price",
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 1)
    )
    db_session_for_tests.add(location_electricity_price)
    db_session_for_tests.commit()

    location_electricity_price_update = LocationElectricityPriceUpdate(
        location_electricity_price_id=location_electricity_price.location_electricity_price_id,
        ended_at=datetime(2024, 1, 2)
    )
    updated_location_electricity_price = location_electricity_prices_service.update_location_electricity_price(location_electricity_price_update)

    assert updated_location_electricity_price.location_electricity_price_id == location_electricity_price.location_electricity_price_id
    assert updated_location_electricity_price.location_id == location_electricity_price.location_id
    assert updated_location_electricity_price.comment == location_electricity_price.comment
    assert updated_location_electricity_price.price_per_kwh == location_electricity_price.price_per_kwh
    assert updated_location_electricity_price.started_at == location_electricity_price.started_at
    assert updated_location_electricity_price.ended_at == location_electricity_price_update.ended_at

    location_electricity_price_from_db = db_session_for_tests.query(LocationElectricityPriceModel).get(location_electricity_price.location_electricity_price_id)
    assert location_electricity_price_from_db is not None
    assert LocationElectricityPrice.model_validate(location_electricity_price_from_db, from_attributes=True) == updated_location_electricity_price


def test_get_current_location_electricity_price_when_resource_exists(db_session_for_tests: Session, location_for_tests: Location):
    """Test that the LocationElectricityPricesService.get_current_location_electricity_price method returns the current resource."""
    location_electricity_prices_service = LocationElectricityPricesService(PostgresLocationElectricityPricesRepository(db_session_for_tests))
    db_session_for_tests.add(LocationElectricityPriceModel(
        location_id=location_for_tests.location_id,
        comment="Test location electricity price 1",
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 1),
        ended_at=datetime(2024, 1, 2)
    ))
    location_electricity_price_model = LocationElectricityPriceModel(
        location_id=location_for_tests.location_id,
        comment="Test location electricity price 2",
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 2)
    )
    db_session_for_tests.add(location_electricity_price_model)
    db_session_for_tests.commit()

    current_location_electricity_price = location_electricity_prices_service.get_current_location_electricity_price(location_for_tests.location_id)

    assert current_location_electricity_price == LocationElectricityPrice.model_validate(location_electricity_price_model, from_attributes=True)


def test_get_current_location_electricity_price_when_resource_doesnt_exist(db_session_for_tests: Session):
    """Test that the LocationElectricityPricesService.get_current_location_electricity_price method returns None when the resource doesn't exist."""
    location_electricity_prices_service = LocationElectricityPricesService(PostgresLocationElectricityPricesRepository(db_session_for_tests))
    location_id = uuid4()

    current_location_electricity_price = location_electricity_prices_service.get_current_location_electricity_price(location_id)

    assert current_location_electricity_price is None


def test_get_location_electricity_prices_returns_all_prices_for_location(db_session_for_tests: Session, location_for_tests: Location, other_location_for_tests: Location):
    """Test that the LocationElectricityPricesService.get_location_electricity_prices method returns all prices for the location."""
    location_electricity_prices_service = LocationElectricityPricesService(PostgresLocationElectricityPricesRepository(db_session_for_tests))
    db_session_for_tests.add(LocationElectricityPriceModel(
        location_id=other_location_for_tests.location_id,
        comment="Test other location electricity price 1",
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 1),
        ended_at=datetime(2024, 1, 2)
    ))
    location_electricity_price_model_1 = LocationElectricityPriceModel(
        location_id=location_for_tests.location_id,
        comment="Test location electricity price 1",
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 1),
        ended_at=datetime(2024, 1, 2)
    )
    location_electricity_price_model_2 = LocationElectricityPriceModel(
        location_id=location_for_tests.location_id,
        comment="Test location electricity price 2",
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 2)
    )
    db_session_for_tests.add_all([location_electricity_price_model_1, location_electricity_price_model_2])
    db_session_for_tests.commit()

    location_electricity_prices = location_electricity_prices_service.get_location_electricity_prices(location_for_tests.location_id, datetime(2023, 1, 1))

    assert len(location_electricity_prices) == 2
    assert LocationElectricityPrice.model_validate(location_electricity_price_model_1, from_attributes=True) in location_electricity_prices
    assert LocationElectricityPrice.model_validate(location_electricity_price_model_2, from_attributes=True) in location_electricity_prices


def test_filter_by_returns_filtered_prices(db_session_for_tests: Session, location_for_tests: Location, other_location_for_tests: Location):
    """Test that the LocationElectricityPricesService.filter_by method returns filtered prices."""
    location_electricity_prices_service = LocationElectricityPricesService(PostgresLocationElectricityPricesRepository(db_session_for_tests))
    db_session_for_tests.add(LocationElectricityPriceModel(
        location_id=other_location_for_tests.location_id,
        comment="Test other location electricity price 1",
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 1),
        ended_at=datetime(2024, 1, 2)
    ))
    location_electricity_price_model_1 = LocationElectricityPriceModel(
        location_id=location_for_tests.location_id,
        comment="Test location electricity price 1",
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 1),
        ended_at=datetime(2024, 1, 2)
    )
    location_electricity_price_model_2 = LocationElectricityPriceModel(
        location_id=location_for_tests.location_id,
        comment="Test location electricity price 2",
        price_per_kwh=0.123,
        started_at=datetime(2024, 1, 2)
    )
    db_session_for_tests.add_all([location_electricity_price_model_1, location_electricity_price_model_2])
    db_session_for_tests.commit()

    location_electricity_prices = location_electricity_prices_service.filter_by(location_id=location_for_tests.location_id)

    assert len(location_electricity_prices) == 2
    assert LocationElectricityPrice.model_validate(location_electricity_price_model_1, from_attributes=True) in location_electricity_prices
    assert LocationElectricityPrice.model_validate(location_electricity_price_model_2, from_attributes=True) in location_electricity_prices
