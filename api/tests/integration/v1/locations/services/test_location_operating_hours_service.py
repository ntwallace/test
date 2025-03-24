from datetime import datetime, time
from uuid import uuid4, UUID

from sqlalchemy.orm import Session

from app.v1.locations.models.location_operating_hours import LocationOperatingHours
from app.v1.locations.repositories.location_operating_hours_repository import PostgresLocationOperatingHoursRepository
from app.v1.locations.repositories.locations_repository import PostgresLocationsRepository
from app.v1.locations.schemas.location import LocationCreate
from app.v1.locations.schemas.location_operating_hours import LocationOperatingHoursCreate, LocationOperatingHoursUpdate
from app.v1.locations.services.location_operating_hours import LocationOperatingHoursService
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import DayOfWeek


def test_create_location_operating_hours_inserts_new_model(db_session_for_tests: Session):
    locations_service = LocationsService(
        locations_repository=PostgresLocationsRepository(db_session_for_tests)
    )
    location_operating_hours_service = LocationOperatingHoursService(
        location_operating_hours_repository=PostgresLocationOperatingHoursRepository(db_session_for_tests)
    )

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
    location = locations_service.create_location(location_create)
    
    location_operating_hours_create = LocationOperatingHoursCreate(
        location_id=location.location_id,
        day_of_week=DayOfWeek.MONDAY,
        is_open=True,
        work_start_time=datetime.now().time(),
        open_time=datetime.now().time(),
        close_time=datetime.now().time(),
        work_end_time=datetime.now().time()
    )
    location_operating_hours = location_operating_hours_service.create_location_operating_hours(location_operating_hours_create)

    location_operating_hours_models = db_session_for_tests.query(LocationOperatingHours).all()
    assert len(location_operating_hours_models) == 1
    location_operating_hours_model = location_operating_hours_models[0]
    assert location_operating_hours_model.location_id == location_operating_hours.location_id
    assert location_operating_hours_model.day_of_week == location_operating_hours.day_of_week
    assert location_operating_hours_model.is_open == location_operating_hours.is_open
    assert location_operating_hours_model.work_start_time == location_operating_hours.work_start_time
    assert location_operating_hours_model.open_time == location_operating_hours.open_time
    assert location_operating_hours_model.close_time == location_operating_hours.close_time
    assert location_operating_hours_model.work_end_time == location_operating_hours.work_end_time
    assert location_operating_hours_model.created_at == location_operating_hours.created_at
    assert location_operating_hours_model.updated_at == location_operating_hours.updated_at


def test_get_location_operating_hours_for_location_returns_list_of_models(db_session_for_tests: Session):
    locations_service = LocationsService(   
        locations_repository=PostgresLocationsRepository(db_session_for_tests)
    )
    location_operating_hours_service = LocationOperatingHoursService(
        location_operating_hours_repository=PostgresLocationOperatingHoursRepository(db_session_for_tests)
    )

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
    location = locations_service.create_location(location_create)
    
    location_operating_hours_create = LocationOperatingHoursCreate(
        location_id=location.location_id,
        day_of_week=DayOfWeek.MONDAY,
        is_open=True,
        work_start_time=datetime.now().time(),
        open_time=datetime.now().time(),
        close_time=datetime.now().time(),
        work_end_time=datetime.now().time()
    )
    location_operating_hours = location_operating_hours_service.create_location_operating_hours(location_operating_hours_create)

    location_operating_hours_models = location_operating_hours_service.get_location_operating_hours_for_location(location.location_id)
    assert len(location_operating_hours_models) == 1
    location_operating_hours_model = location_operating_hours_models[0]
    assert location_operating_hours_model.location_id == location_operating_hours.location_id
    assert location_operating_hours_model.day_of_week == location_operating_hours.day_of_week
    assert location_operating_hours_model.is_open == location_operating_hours.is_open
    assert location_operating_hours_model.work_start_time == location_operating_hours.work_start_time
    assert location_operating_hours_model.open_time == location_operating_hours.open_time
    assert location_operating_hours_model.close_time == location_operating_hours.close_time
    assert location_operating_hours_model.work_end_time == location_operating_hours.work_end_time
    assert location_operating_hours_model.created_at == location_operating_hours.created_at
    assert location_operating_hours_model.updated_at == location_operating_hours.updated_at


def test_update_location_operating_hours_updates_record(db_session_for_tests):
    locations_service = LocationsService(   
        locations_repository=PostgresLocationsRepository(db_session_for_tests)
    )
    location_operating_hours_service = LocationOperatingHoursService(
        location_operating_hours_repository=PostgresLocationOperatingHoursRepository(db_session_for_tests)
    )
    
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
    location = locations_service.create_location(location_create)
    
    location_operating_hours_create = LocationOperatingHoursCreate(
        location_id=location.location_id,
        day_of_week=DayOfWeek.MONDAY,
        is_open=True,
        work_start_time=datetime.now().time(),
        open_time=datetime.now().time(),
        close_time=datetime.now().time(),
        work_end_time=datetime.now().time()
    )
    location_operating_hours = location_operating_hours_service.create_location_operating_hours(location_operating_hours_create)

    location_operating_hours_update = LocationOperatingHoursUpdate(
        location_id=location.location_id,
        day_of_week=DayOfWeek.MONDAY,
        is_open=True,
        work_start_time=time(1, 0, 0),
        open_time=time(2, 0, 0),
        close_time=time(3, 0, 0),
        work_end_time=time(4, 0, 0)
    )
    location_operating_hours_updated = location_operating_hours_service.update_location_operating_hours(location_operating_hours_update)

    location_operating_hours_models = location_operating_hours_service.get_location_operating_hours_for_location(location.location_id)
    assert len(location_operating_hours_models) == 1
    location_operating_hours_model = location_operating_hours_models[0]
    assert location_operating_hours_model.location_id == location_operating_hours_updated.location_id
    assert location_operating_hours_model.day_of_week == location_operating_hours_updated.day_of_week
    assert location_operating_hours_model.is_open == location_operating_hours_updated.is_open
    assert location_operating_hours_model.work_start_time == location_operating_hours_updated.work_start_time
    assert location_operating_hours_model.open_time == location_operating_hours_updated.open_time
    assert location_operating_hours_model.close_time == location_operating_hours_updated.close_time
    assert location_operating_hours_model.work_end_time == location_operating_hours_updated.work_end_time
    assert location_operating_hours_model.created_at == location_operating_hours_updated.created_at
    assert location_operating_hours_model.updated_at == location_operating_hours_updated.updated_at


def test_delete_location_operating_hours_for_location_deletes_all_records_for_location(db_session_for_tests):
    locations_service = LocationsService(   
        locations_repository=PostgresLocationsRepository(db_session_for_tests)
    )
    location_operating_hours_service = LocationOperatingHoursService(
        location_operating_hours_repository=PostgresLocationOperatingHoursRepository(db_session_for_tests)
    )
    
    location = locations_service.create_location(
        LocationCreate(
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
    )
    location_operating_hours_service.create_location_operating_hours(
        LocationOperatingHoursCreate(
            location_id=location.location_id,
            day_of_week=DayOfWeek.MONDAY,
            is_open=True,
            work_start_time=datetime.now().time(),
            open_time=datetime.now().time(),
            close_time=datetime.now().time(),
            work_end_time=datetime.now().time()
        )
    )
    location_operating_hours_service.create_location_operating_hours(
        LocationOperatingHoursCreate(
            location_id=location.location_id,
            day_of_week=DayOfWeek.TUESDAY,
            is_open=True,
            work_start_time=datetime.now().time(),
            open_time=datetime.now().time(),
            close_time=datetime.now().time(),
            work_end_time=datetime.now().time()
        )
    )
    location_operating_hours = location_operating_hours_service.get_location_operating_hours_for_location(location.location_id)
    assert len(location_operating_hours) == 2
    location_operating_hours_service.delete_location_operating_hours_for_location(location.location_id)
    location_operating_hours = location_operating_hours_service.get_location_operating_hours_for_location(location.location_id)
    assert len(location_operating_hours) == 0
