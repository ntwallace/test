from uuid import uuid4, UUID

from sqlalchemy.orm import Session

from app.v1.locations.models.location import Location
from app.v1.locations.repositories.locations_repository import PostgresLocationsRepository
from app.v1.locations.schemas.location import LocationCreate


def test_create_inserts_new_model(db_session_for_tests: Session):
    locations_repository = PostgresLocationsRepository(db_session_for_tests)

    location_create = LocationCreate(
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
    )
    location = locations_repository.create(location_create)
    
    location_models = db_session_for_tests.query(Location).all()
    assert len(location_models) == 1
    location_model = location_models[0]
    assert location_model.location_id == location.location_id
    assert location_model.name == location_create.name
    assert location_model.address == location_create.address
    assert location_model.city == location_create.city
    assert location_model.state == location_create.state
    assert location_model.zip_code == location_create.zip_code
    assert location_model.country == location_create.country
    assert location_model.timezone == location_create.timezone
    assert location_model.latitude == location_create.latitude
    assert location_model.longitude == location_create.longitude
    assert location_model.organization_id == location_create.organization_id
    assert location_model.created_at == location.created_at
    assert location_model.updated_at == location.updated_at


def test_get_returns_location(db_session_for_tests: Session):
    locations_repository = PostgresLocationsRepository(db_session_for_tests)

    location_create = LocationCreate(
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
    )
    location = locations_repository.create(location_create)

    other_location_create = LocationCreate(
        name='Other Location',
        address='123 Other St',
        city='Other City',
        state='OS',
        zip_code='54321',
        country='Other Country',
        timezone='Other Timezone',
        latitude=1.0,
        longitude=1.0,
        organization_id=uuid4()
    )
    locations_repository.create(other_location_create)

    retrieved_location = locations_repository.get(location.location_id)
    assert retrieved_location.location_id == location.location_id
    assert retrieved_location.name == location.name
    assert retrieved_location.address == location.address
    assert retrieved_location.city == location.city
    assert retrieved_location.state == location.state
    assert retrieved_location.zip_code == location.zip_code
    assert retrieved_location.country == location.country
    assert retrieved_location.timezone == location.timezone
    assert retrieved_location.latitude == location.latitude
    assert retrieved_location.longitude == location.longitude
    assert retrieved_location.created_at == location.created_at
    assert retrieved_location.updated_at == location.updated_at


def test_get_location_returns_none_if_location_does_not_exist(db_session_for_tests: Session):
    locations_repository = PostgresLocationsRepository(db_session_for_tests)

    retrieved_location = locations_repository.get(uuid4())
    assert retrieved_location is None


def test_filter_by_returns_relevant_locations(db_session_for_tests: Session):
    locations_repository = PostgresLocationsRepository(db_session_for_tests)

    organization_id = uuid4()

    location_create = LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Test City',
        state='TS',
        zip_code='12345',
        country='Test Country',
        timezone='Test Timezone',
        latitude=0.0,
        longitude=0.0,
        organization_id=organization_id
    )
    location = locations_repository.create(location_create)

    other_location_create = LocationCreate(
        name='Other Location',
        address='123 Other St',
        city='Other City',
        state='OS',
        zip_code='54321',
        country='Other Country',
        timezone='Other Timezone',
        latitude=1.0,
        longitude=1.0,
        organization_id=uuid4()
    )
    locations_repository.create(other_location_create)

    locations = locations_repository.filter_by(organization_id=organization_id)
    assert len(locations) == 1
    assert locations[0].location_id == location.location_id
    assert locations[0].name == location.name
    assert locations[0].address == location.address
    assert locations[0].city == location.city
    assert locations[0].state == location.state
    assert locations[0].zip_code == location.zip_code
    assert locations[0].country == location.country
    assert locations[0].timezone == location.timezone
    assert locations[0].latitude == location.latitude
    assert locations[0].longitude == location.longitude
    assert locations[0].created_at == location.created_at
    assert locations[0].updated_at == location.updated_at
    assert locations[0].organization_id == location.organization_id


def test_filter_by_returns_empty_list_if_no_locations_exist(db_session_for_tests: Session):
    locations_repository = PostgresLocationsRepository(db_session_for_tests)

    location_create = LocationCreate(
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
    )
    locations_repository.create(location_create)

    locations = locations_repository.filter_by(organization_id=uuid4())
    assert len(locations) == 0
