from uuid import uuid4, UUID
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.hvac.models.hvac_zone import HvacZone
from app.v1.hvac.repositories.hvac_zones_repository import PostgresHvacZonesRepository
from app.v1.hvac.schemas.hvac_zone import HvacZoneCreate
from app.v1.hvac.services.hvac_zones import HvacZonesService


def test_create_hvac_zones_inserts_new_model(db_session_for_tests: Session):
    service = HvacZonesService(
        hvac_zones_repository=PostgresHvacZonesRepository(db_session_for_tests)
    )

    hvac_zones_create = HvacZoneCreate(
        name='Test HVAC Zone',
        hvac_zone_id=uuid4(),
        location_id=uuid4()
    )
    hvac_zones = service.create_hvac_zone(hvac_zones_create)

    hvac_zones_models = db_session_for_tests.query(HvacZone).all()
    assert len(hvac_zones_models) == 1
    hvac_zones_model = hvac_zones_models[0]
    assert hvac_zones_model.name == hvac_zones.name
    assert hvac_zones_model.hvac_zone_id == hvac_zones.hvac_zone_id
    assert hvac_zones_model.location_id == hvac_zones.location_id
    assert hvac_zones_model.created_at == hvac_zones.created_at
    assert hvac_zones_model.updated_at == hvac_zones.updated_at


def test_create_hvac_zones_raises_error_if_hvac_zones_exists(db_session_for_tests: Session):
    service = HvacZonesService(
        hvac_zones_repository=PostgresHvacZonesRepository(db_session_for_tests)
    )

    hvac_zones_create = HvacZoneCreate(
        name='Test HVAC Zone',
        hvac_zone_id=uuid4(),
        location_id=uuid4()
    )
    service.create_hvac_zone(hvac_zones_create)
    with pytest.raises(ValueError):
        service.create_hvac_zone(hvac_zones_create)


def test_get_hvac_zones_returns_correct_model(db_session_for_tests: Session):
    service = HvacZonesService(
        hvac_zones_repository=PostgresHvacZonesRepository(db_session_for_tests)
    )

    hvac_zones_create = HvacZoneCreate(
        name='Test HVAC Zone',
        hvac_zone_id=uuid4(),
        location_id=uuid4()
    )
    hvac_zones = service.create_hvac_zone(hvac_zones_create)

    hvac_zones_model = service.get_hvac_zone_by_id(hvac_zones.hvac_zone_id)
    assert hvac_zones_model.name == hvac_zones.name
    assert hvac_zones_model.hvac_zone_id == hvac_zones.hvac_zone_id
    assert hvac_zones_model.location_id == hvac_zones.location_id
    assert hvac_zones_model.created_at == hvac_zones.created_at
    assert hvac_zones_model.updated_at == hvac_zones.updated_at


def test_get_hvac_zones_returns_none_if_hvac_zones_does_not_exist(db_session_for_tests: Session):
    service = HvacZonesService(
        hvac_zones_repository=PostgresHvacZonesRepository(db_session_for_tests)
    )

    hvac_zones_model = service.get_hvac_zone_by_id(uuid4())
    assert hvac_zones_model is None


def test_get_hvac_zone_by_attributes_returns_correct_model(db_session_for_tests: Session):
    service = HvacZonesService(
        hvac_zones_repository=PostgresHvacZonesRepository(db_session_for_tests)
    )

    hvac_zones_create = HvacZoneCreate(
        name='Test HVAC Zone',
        hvac_zone_id=uuid4(),
        location_id=uuid4()
    )
    hvac_zones = service.create_hvac_zone(hvac_zones_create)

    hvac_zones_model = service.get_hvac_zone_by_attributes(hvac_zones.name, hvac_zones.location_id)
    assert hvac_zones_model.name == hvac_zones.name
    assert hvac_zones_model.hvac_zone_id == hvac_zones.hvac_zone_id
    assert hvac_zones_model.location_id == hvac_zones.location_id
    assert hvac_zones_model.created_at == hvac_zones.created_at
    assert hvac_zones_model.updated_at == hvac_zones.updated_at


def test_get_hvac_zones_by_location_id_returns_correct_models(db_session_for_tests: Session):
    service = HvacZonesService(
        hvac_zones_repository=PostgresHvacZonesRepository(db_session_for_tests)
    )

    hvac_zones_create = HvacZoneCreate(
        name='Test HVAC Zone',
        hvac_zone_id=uuid4(),
        location_id=uuid4()
    )
    hvac_zones = service.create_hvac_zone(hvac_zones_create)

    hvac_zones_models = service.get_hvac_zones_by_location_id(hvac_zones.location_id)
    assert len(hvac_zones_models) == 1
    hvac_zones_model = hvac_zones_models[0]
    assert hvac_zones_model.name == hvac_zones.name
    assert hvac_zones_model.hvac_zone_id == hvac_zones.hvac_zone_id
    assert hvac_zones_model.location_id == hvac_zones.location_id
    assert hvac_zones_model.created_at == hvac_zones.created_at
    assert hvac_zones_model.updated_at == hvac_zones.updated_at


def test_get_hvac_zones_by_location_id_returns_empty_list_if_no_hvac_zones_exist(db_session_for_tests: Session):
    service = HvacZonesService(
        hvac_zones_repository=PostgresHvacZonesRepository(db_session_for_tests)
    )

    hvac_zones_models = service.get_hvac_zones_by_location_id(uuid4())
    assert len(hvac_zones_models) == 0


def test_delete_hvac_zone_deletes_model(db_session_for_tests: Session):
    service = HvacZonesService(
        hvac_zones_repository=PostgresHvacZonesRepository(db_session_for_tests)
    )

    hvac_zones_create = HvacZoneCreate(
        name='Test HVAC Zone',
        hvac_zone_id=uuid4(),
        location_id=uuid4()
    )
    hvac_zones = service.create_hvac_zone(hvac_zones_create)

    service.delete_hvac_zone(hvac_zones.hvac_zone_id)
    hvac_zones_models = db_session_for_tests.query(HvacZone).all()
    assert len(hvac_zones_models) == 0
