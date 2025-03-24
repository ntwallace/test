from uuid import uuid4, UUID
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.hvac.models.hvac_zone_equipment import HvacZoneEquipment
from app.v1.hvac.repositories.hvac_zone_equipment_repository import PostgresHvacZoneEquipmentRepository
from app.v1.hvac.schemas.hvac_zone_equipment import HvacZoneEquipmentCreate
from app.v1.hvac.services.hvac_zone_equipment import HvacZoneEquipmentService


def test_create_hvac_zone_equipment_inserts_new_model(db_session_for_tests: Session):
    service = HvacZoneEquipmentService(
        PostgresHvacZoneEquipmentRepository(db_session_for_tests)
    )

    hvac_zone_equipment_create = HvacZoneEquipmentCreate(
        hvac_zone_id=uuid4(),
        hvac_equipment_type_id=uuid4(),
        circuit_id=uuid4(),
        serial='Test Serial'
    )
    hvac_zone_equipment = service.create_hvac_zone_equipment(hvac_zone_equipment_create)

    hvac_zone_equipment_models = db_session_for_tests.query(HvacZoneEquipment).all()
    assert len(hvac_zone_equipment_models) == 1
    hvac_zone_equipment_model = hvac_zone_equipment_models[0]
    assert hvac_zone_equipment_model.hvac_zone_id == hvac_zone_equipment.hvac_zone_id
    assert hvac_zone_equipment_model.hvac_equipment_type_id == hvac_zone_equipment.hvac_equipment_type_id
    assert hvac_zone_equipment_model.circuit_id == hvac_zone_equipment.circuit_id
    assert hvac_zone_equipment_model.serial == hvac_zone_equipment.serial
    assert hvac_zone_equipment_model.hvac_zone_equipment_id == hvac_zone_equipment.hvac_zone_equipment_id
    assert hvac_zone_equipment_model.created_at == hvac_zone_equipment.created_at
    assert hvac_zone_equipment_model.updated_at == hvac_zone_equipment.updated_at


def test_create_hvac_zone_equipment_inserts_new_model_nulls(db_session_for_tests: Session):
    service = HvacZoneEquipmentService(
        PostgresHvacZoneEquipmentRepository(db_session_for_tests)
    )

    hvac_zone_equipment_create = HvacZoneEquipmentCreate(hvac_zone_id=uuid4(), hvac_equipment_type_id=uuid4(), circuit_id=uuid4())
    hvac_zone_equipment = service.create_hvac_zone_equipment(hvac_zone_equipment_create)

    hvac_zone_equipment_models = db_session_for_tests.query(HvacZoneEquipment).all()
    assert len(hvac_zone_equipment_models) == 1
    hvac_zone_equipment_model = hvac_zone_equipment_models[0]
    assert hvac_zone_equipment_model.hvac_zone_id == hvac_zone_equipment.hvac_zone_id
    assert hvac_zone_equipment_model.hvac_equipment_type_id == hvac_zone_equipment.hvac_equipment_type_id
    assert hvac_zone_equipment_model.circuit_id == hvac_zone_equipment.circuit_id
    assert hvac_zone_equipment_model.serial is None
    assert hvac_zone_equipment_model.hvac_zone_equipment_id == hvac_zone_equipment.hvac_zone_equipment_id
    assert hvac_zone_equipment_model.created_at == hvac_zone_equipment.created_at
    assert hvac_zone_equipment_model.updated_at == hvac_zone_equipment.updated_at


def test_create_hvac_zone_equipment_raises_error_if_hvac_zone_equipment_exists(db_session_for_tests: Session):
    service = HvacZoneEquipmentService(
        PostgresHvacZoneEquipmentRepository(db_session_for_tests)
    )

    hvac_zone_equipment_create = HvacZoneEquipmentCreate(
        hvac_zone_id=uuid4(),
        hvac_equipment_type_id=uuid4(),
        circuit_id=uuid4(),
        serial='Test Serial'
    )
    service.create_hvac_zone_equipment(hvac_zone_equipment_create)

    with pytest.raises(IntegrityError):
        service.create_hvac_zone_equipment(hvac_zone_equipment_create)


def test_get_hvac_zone_equipment_by_id_returns_hvac_zone_equipment(db_session_for_tests: Session):
    service = HvacZoneEquipmentService(
        PostgresHvacZoneEquipmentRepository(db_session_for_tests)
    )

    hvac_zone_equipment_create = HvacZoneEquipmentCreate(
        hvac_zone_id=uuid4(),
        hvac_equipment_type_id=uuid4(),
        circuit_id=uuid4(),
        serial='Test Serial'
    )
    hvac_zone_equipment = service.create_hvac_zone_equipment(hvac_zone_equipment_create)

    hvac_zone_equipment_by_id = service.get_hvac_zone_equipment_by_id(hvac_zone_equipment.hvac_zone_equipment_id)
    assert hvac_zone_equipment_by_id.hvac_zone_equipment_id == hvac_zone_equipment.hvac_zone_equipment_id
    assert hvac_zone_equipment_by_id.hvac_zone_id == hvac_zone_equipment.hvac_zone_id
    assert hvac_zone_equipment_by_id.hvac_equipment_type_id == hvac_zone_equipment.hvac_equipment_type_id
    assert hvac_zone_equipment_by_id.circuit_id == hvac_zone_equipment.circuit_id
    assert hvac_zone_equipment_by_id.serial == hvac_zone_equipment.serial
    assert hvac_zone_equipment_by_id.created_at == hvac_zone_equipment.created_at
    assert hvac_zone_equipment_by_id.updated_at == hvac_zone_equipment.updated_at


def test_get_hvac_zone_equipment_by_id_returns_none_if_hvac_zone_equipment_does_not_exist(db_session_for_tests: Session):
    service = HvacZoneEquipmentService(
        PostgresHvacZoneEquipmentRepository(db_session_for_tests)
    )

    hvac_zone_equipment_by_id = service.get_hvac_zone_equipment_by_id(uuid4())
    assert hvac_zone_equipment_by_id is None


def test_get_hvac_zone_equipment_by_attributes_returns_hvac_zone_equipment(db_session_for_tests: Session):
    service = HvacZoneEquipmentService(
        PostgresHvacZoneEquipmentRepository(db_session_for_tests)
    )

    hvac_zone_equipment_create = HvacZoneEquipmentCreate(
        hvac_zone_id=uuid4(),
        hvac_equipment_type_id=uuid4(),
        circuit_id=uuid4(),
        serial='Test Serial'
    )
    hvac_zone_equipment = service.create_hvac_zone_equipment(hvac_zone_equipment_create)

    hvac_zone_equipment_by_attributes = service.get_hvac_zone_equipment_by_attributes(hvac_zone_equipment.hvac_zone_id, hvac_zone_equipment.hvac_equipment_type_id)
    assert hvac_zone_equipment_by_attributes.hvac_zone_equipment_id == hvac_zone_equipment.hvac_zone_equipment_id
    assert hvac_zone_equipment_by_attributes.hvac_zone_id == hvac_zone_equipment.hvac_zone_id
    assert hvac_zone_equipment_by_attributes.hvac_equipment_type_id == hvac_zone_equipment.hvac_equipment_type_id
    assert hvac_zone_equipment_by_attributes.circuit_id == hvac_zone_equipment.circuit_id
    assert hvac_zone_equipment_by_attributes.serial == hvac_zone_equipment.serial
    assert hvac_zone_equipment_by_attributes.created_at == hvac_zone_equipment.created_at
    assert hvac_zone_equipment_by_attributes.updated_at == hvac_zone_equipment.updated_at


def test_get_hvac_zone_equipment_by_attributes_returns_none_if_hvac_zone_equipment_does_not_exist(db_session_for_tests: Session):
    service = HvacZoneEquipmentService(
        PostgresHvacZoneEquipmentRepository(db_session_for_tests)
    )

    hvac_zone_equipment_by_attributes = service.get_hvac_zone_equipment_by_attributes(uuid4(), uuid4())
    assert hvac_zone_equipment_by_attributes is None


def test_get_hvac_zone_equipment_by_hvac_zone_id_returns_list_of_hvac_zone_equipment(db_session_for_tests: Session):
    service = HvacZoneEquipmentService(
        PostgresHvacZoneEquipmentRepository(db_session_for_tests)
    )

    hvac_zone_id = uuid4()
    hvac_zone_equipment_create = HvacZoneEquipmentCreate(
        hvac_zone_id=hvac_zone_id,
        hvac_equipment_type_id=uuid4(),
        circuit_id=uuid4(),
        serial='Test Serial'
    )
    hvac_zone_equipment = service.create_hvac_zone_equipment(hvac_zone_equipment_create)

    hvac_zone_equipment_by_hvac_zone_id = service.get_hvac_zone_equipment_by_hvac_zone_id(hvac_zone_id)
    assert len(hvac_zone_equipment_by_hvac_zone_id) == 1
    assert hvac_zone_equipment_by_hvac_zone_id[0].hvac_zone_equipment_id == hvac_zone_equipment.hvac_zone_equipment_id
    assert hvac_zone_equipment_by_hvac_zone_id[0].hvac_zone_id == hvac_zone_equipment.hvac_zone_id
    assert hvac_zone_equipment_by_hvac_zone_id[0].hvac_equipment_type_id == hvac_zone_equipment.hvac_equipment_type_id
    assert hvac_zone_equipment_by_hvac_zone_id[0].circuit_id == hvac_zone_equipment.circuit_id
    assert hvac_zone_equipment_by_hvac_zone_id[0].serial == hvac_zone_equipment.serial
    assert hvac_zone_equipment_by_hvac_zone_id[0].created_at == hvac_zone_equipment.created_at
    assert hvac_zone_equipment_by_hvac_zone_id[0].updated_at == hvac_zone_equipment.updated_at


def test_get_hvac_zone_equipment_by_hvac_zone_id_returns_empty_list_if_no_hvac_zone_equipment(db_session_for_tests: Session):
    service = HvacZoneEquipmentService(
        PostgresHvacZoneEquipmentRepository(db_session_for_tests)
    )

    hvac_zone_equipment_by_hvac_zone_id = service.get_hvac_zone_equipment_by_hvac_zone_id(uuid4())
    assert len(hvac_zone_equipment_by_hvac_zone_id) == 0


def test_delete_hvac_zone_equipment_deletes_hvac_zone_equipment(db_session_for_tests: Session):
    service = HvacZoneEquipmentService(
        PostgresHvacZoneEquipmentRepository(db_session_for_tests)
    )

    hvac_zone_equipment_create = HvacZoneEquipmentCreate(
        hvac_zone_id=uuid4(),
        hvac_equipment_type_id=uuid4(),
        circuit_id=uuid4(),
        serial='Test Serial'
    )
    hvac_zone_equipment = service.create_hvac_zone_equipment(hvac_zone_equipment_create)

    service.delete_hvac_zone_equipment(hvac_zone_equipment.hvac_zone_equipment_id)
    hvac_zone_equipment_by_id = service.get_hvac_zone_equipment_by_id(hvac_zone_equipment.hvac_zone_equipment_id)
    assert hvac_zone_equipment_by_id is None
