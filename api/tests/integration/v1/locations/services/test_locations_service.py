from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from app.v1.locations.models.location import Location as LocationModel
from app.v1.locations.repositories.locations_repository import PostgresLocationsRepository
from app.v1.locations.schemas.location import LocationCreate
from app.v1.locations.services.locations import LocationsService

def test_create_location_inserts_new_model(db_session_for_tests: Session):
    locations_service = LocationsService(PostgresLocationsRepository(db_session_for_tests))

    # Create LocationCreate
    location_create = LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Milwaukee',
        state='WI',
        zip_code='12345',
        country='USA',
        latitude=43.0389,
        longitude=-87.9065,
        timezone='America/Chicago',
        organization_id=uuid4()
    )
    location = locations_service.create_location(location_create)

    assert location.name == location_create.name

    location_models = db_session_for_tests.query(LocationModel).all()
    assert len(location_models) == 1
    location_model = location_models[0]
    assert location_model.name == location_create.name
    assert isinstance(location_model.location_id, UUID)
    assert isinstance(location_model.created_at, datetime)
    assert isinstance(location_model.updated_at, datetime)


def test_get_location_returns_location(db_session_for_tests: Session):
    locations_service = LocationsService(PostgresLocationsRepository(db_session_for_tests))

    location_create = LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Milwaukee',
        state='WI',
        zip_code='12345',
        country='USA',
        latitude=43.0389,
        longitude=-87.9065,
        timezone='America/Chicago',
        organization_id=uuid4()
    )
    location = locations_service.create_location(location_create)

    location = locations_service.get_location(location.location_id)

    assert location.name == location_create.name


def test_get_location_returns_none_when_location_doesnt_exist(db_session_for_tests: Session):
    locations_service = LocationsService(PostgresLocationsRepository(db_session_for_tests))

    location_create = LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Milwaukee',
        state='WI',
        zip_code='12345',
        country='USA',
        latitude=43.0389,
        longitude=-87.9065,
        timezone='America/Chicago',
        organization_id=uuid4()
    )
    locations_service.create_location(location_create)
    location = locations_service.get_location(uuid4())

    assert location is None


def test_get_locations_by_organization_id_returns_list_of_locations(db_session_for_tests: Session):
    locations_service = LocationsService(PostgresLocationsRepository(db_session_for_tests))

    organization_id = uuid4()
    location_create = LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Milwaukee',
        state='WI',
        zip_code='12345',
        country='USA',
        latitude=43.0389,
        longitude=-87.9065,
        timezone='America/Chicago',
        organization_id=organization_id
    )
    location = locations_service.create_location(location_create)

    locations = locations_service.get_locations_by_organization_id(organization_id)

    assert len(locations) == 1
    location = locations[0]
    assert location.name == location_create.name


def test_get_locations_by_organization_id_returns_empty_list_when_no_locations_exist_for_organization(db_session_for_tests: Session):
    locations_service = LocationsService(PostgresLocationsRepository(db_session_for_tests))

    organization_id = uuid4()
    location_create = LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Milwaukee',
        state='WI',
        zip_code='12345',
        country='USA',
        latitude=43.0389,
        longitude=-87.9065,
        timezone='America/Chicago',
        organization_id=organization_id
    )
    locations_service.create_location(location_create)

    locations = locations_service.get_locations_by_organization_id(uuid4())

    assert len(locations) == 0


def test_filter_by_returns_list_of_locations(db_session_for_tests: Session):
    locations_service = LocationsService(PostgresLocationsRepository(db_session_for_tests))

    organization_id = uuid4()
    location_create = LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Milwaukee',
        state='WI',
        zip_code='12345',
        country='USA',
        latitude=43.0389,
        longitude=-87.9065,
        timezone='America/Chicago',
        organization_id=organization_id
    )
    location = locations_service.create_location(location_create)

    locations = locations_service.filter_by(organization_id=organization_id)

    assert len(locations) == 1
    location = locations[0]
    assert location.name == location_create.name


def test_filter_by_returns_empty_list_when_no_locations_exist_for_organization(db_session_for_tests: Session):
    locations_service = LocationsService(PostgresLocationsRepository(db_session_for_tests))

    organization_id = uuid4()
    location_create = LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Milwaukee',
        state='WI',
        zip_code='12345',
        country='USA',
        latitude=43.0389,
        longitude=-87.9065,
        timezone='America/Chicago',
        organization_id=organization_id
    )
    locations_service.create_location(location_create)

    locations = locations_service.filter_by(organization_id=uuid4())

    assert len(locations) == 0


def test_filter_by_returns_list_when_filter_by_name(db_session_for_tests: Session):
    locations_service = LocationsService(PostgresLocationsRepository(db_session_for_tests))

    organization_id = uuid4()
    location_create = LocationCreate(
        name='Test Location',
        address='123 Test St',
        city='Milwaukee',
        state='WI',
        zip_code='12345',
        country='USA',
        latitude=43.0389,
        longitude=-87.9065,
        timezone='America/Chicago',
        organization_id=organization_id
    )
    location = locations_service.create_location(location_create)

    locations = locations_service.filter_by(name='Test Location')

    assert len(locations) == 1
    location = locations[0]
    assert location.name == location_create.name
