from uuid import uuid4, UUID
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.hvac.models.hvac_equipment_type import HvacEquipmentTypes
from app.v1.hvac.repositories.hvac_equipment_types_repository import PostgresHvacEquipmentTypesRepository
from app.v1.hvac.schemas.hvac_equipment_type import HvacEquipmentTypeCreate
from app.v1.hvac.services.hvac_equipment_types import HvacEquipmentTypesService


def test_create_hvac_equipment_type_inserts_new_model(db_session_for_tests: Session):
    service = HvacEquipmentTypesService(
        hvac_equipment_types_repository=PostgresHvacEquipmentTypesRepository(db_session_for_tests)
    )

    hvac_equipment_type_create = HvacEquipmentTypeCreate(
        make='Test Hvac Equipment',
        model='Test Model',
        type='Test Type',
        subtype='Test Sub Type',
        year_manufactured=2022
    )
    hvac_equipment_type = service.create_hvac_equipment_type(hvac_equipment_type_create)

    hvac_equipment_type_models = db_session_for_tests.query(HvacEquipmentTypes).all()
    assert len(hvac_equipment_type_models) == 1
    hvac_equipment_type_model = hvac_equipment_type_models[0]
    assert hvac_equipment_type_model.make == hvac_equipment_type.make
    assert hvac_equipment_type_model.model == hvac_equipment_type.model
    assert hvac_equipment_type_model.type == hvac_equipment_type.type
    assert hvac_equipment_type_model.subtype == hvac_equipment_type.subtype
    assert hvac_equipment_type_model.year_manufactured == hvac_equipment_type.year_manufactured
    assert hvac_equipment_type_model.hvac_equipment_type_id == hvac_equipment_type.hvac_equipment_type_id
    assert hvac_equipment_type_model.created_at == hvac_equipment_type.created_at
    assert hvac_equipment_type_model.updated_at == hvac_equipment_type.updated_at


def test_create_hvac_equipment_type_inserts_new_model_nulls(db_session_for_tests: Session):
    service = HvacEquipmentTypesService(
        hvac_equipment_types_repository=PostgresHvacEquipmentTypesRepository(db_session_for_tests)    
    )

    hvac_equipment_type_create = HvacEquipmentTypeCreate(make='Test Hvac Equipment 2', type='Test Type 2')
    hvac_equipment_type = service.create_hvac_equipment_type(hvac_equipment_type_create)

    hvac_equipment_type_models = db_session_for_tests.query(HvacEquipmentTypes).all()
    assert len(hvac_equipment_type_models) == 1
    hvac_equipment_type_model = hvac_equipment_type_models[0]
    assert hvac_equipment_type_model.make == hvac_equipment_type.make
    assert hvac_equipment_type_model.model is None
    assert hvac_equipment_type_model.type == hvac_equipment_type.type
    assert hvac_equipment_type_model.subtype is None
    assert hvac_equipment_type_model.year_manufactured is None
    assert hvac_equipment_type_model.hvac_equipment_type_id == hvac_equipment_type.hvac_equipment_type_id
    assert hvac_equipment_type_model.created_at == hvac_equipment_type.created_at
    assert hvac_equipment_type_model.updated_at == hvac_equipment_type.updated_at


def test_create_hvac_equipment_type_raises_error_if_hvac_equipment_type_exists(db_session_for_tests: Session):
    service = HvacEquipmentTypesService(
        hvac_equipment_types_repository=PostgresHvacEquipmentTypesRepository(db_session_for_tests)    
    )

    hvac_equipment_type_create = HvacEquipmentTypeCreate(
        make='Test Hvac Equipment',
        model='Test Model',
        type='Test Type',
        subtype='Test Sub Type',
        year_manufactured=2022
    )
    service.create_hvac_equipment_type(hvac_equipment_type_create)

    with pytest.raises(IntegrityError):
        service.create_hvac_equipment_type(hvac_equipment_type_create)


def test_get_hvac_equipment_type_by_hvac_equipment_type_id_returns_hvac_equipment_type(db_session_for_tests: Session):
    service = HvacEquipmentTypesService(
        hvac_equipment_types_repository=PostgresHvacEquipmentTypesRepository(db_session_for_tests)    
    )

    hvac_equipment_type_create = HvacEquipmentTypeCreate(
        make='Test Hvac Equipment',
        model='Test Model',
        type='Test Type',
        subtype='Test Sub Type',
        year_manufactured=2022
    )
    hvac_equipment_type = service.create_hvac_equipment_type(hvac_equipment_type_create)

    retrieved_hvac_equipment_type = service.get_hvac_equipment_type_by_id(hvac_equipment_type.hvac_equipment_type_id)
    assert retrieved_hvac_equipment_type.make == hvac_equipment_type.make
    assert retrieved_hvac_equipment_type.model == hvac_equipment_type.model
    assert retrieved_hvac_equipment_type.type == hvac_equipment_type.type
    assert retrieved_hvac_equipment_type.subtype == hvac_equipment_type.subtype
    assert retrieved_hvac_equipment_type.year_manufactured == hvac_equipment_type.year_manufactured
    assert retrieved_hvac_equipment_type.hvac_equipment_type_id == hvac_equipment_type.hvac_equipment_type_id
    assert retrieved_hvac_equipment_type.created_at == hvac_equipment_type.created_at
    assert retrieved_hvac_equipment_type.updated_at == hvac_equipment_type.updated_at


def test_get_hvac_equipment_type_by_id_returns_none_if_hvac_equipment_type_does_not_exist(db_session_for_tests: Session):
    service = HvacEquipmentTypesService(
        hvac_equipment_types_repository=PostgresHvacEquipmentTypesRepository(db_session_for_tests)    
    )

    retrieved_hvac_equipment_type = service.get_hvac_equipment_type_by_id(uuid4())
    assert retrieved_hvac_equipment_type is None


def test_get_hvac_equipment_by_make_model_type_subtype_year_returns_hvac_equipment_type(db_session_for_tests: Session):
    service = HvacEquipmentTypesService(
        hvac_equipment_types_repository=PostgresHvacEquipmentTypesRepository(db_session_for_tests)    
    )

    hvac_equipment_type_create = HvacEquipmentTypeCreate(
        make='Test Hvac Equipment',
        model='Test Model',
        type='Test Type',
        subtype='Test Sub Type',
        year_manufactured=2022
    )
    hvac_equipment_type = service.create_hvac_equipment_type(hvac_equipment_type_create)

    retrieved_hvac_equipment_type = service.get_hvac_equipment_type_by_make_model_type_subtype_year(hvac_equipment_type_create.make, hvac_equipment_type_create.model, hvac_equipment_type_create.type, hvac_equipment_type_create.subtype, hvac_equipment_type_create.year_manufactured)

    assert retrieved_hvac_equipment_type.make == hvac_equipment_type.make
    assert retrieved_hvac_equipment_type.model == hvac_equipment_type.model
    assert retrieved_hvac_equipment_type.type == hvac_equipment_type.type
    assert retrieved_hvac_equipment_type.subtype == hvac_equipment_type.subtype
    assert retrieved_hvac_equipment_type.year_manufactured == hvac_equipment_type.year_manufactured
    assert retrieved_hvac_equipment_type.hvac_equipment_type_id == hvac_equipment_type.hvac_equipment_type_id
    assert retrieved_hvac_equipment_type.created_at == hvac_equipment_type.created_at
    assert retrieved_hvac_equipment_type.updated_at == hvac_equipment_type.updated_at


def test_get_hvac_equipment_by_make_model_type_subtype_year_returns_none_if_hvac_equipment_type_does_not_exist(db_session_for_tests: Session):
    service = HvacEquipmentTypesService(
        hvac_equipment_types_repository=PostgresHvacEquipmentTypesRepository(db_session_for_tests)    
    )

    retrieved_hvac_equipment_type = service.get_hvac_equipment_type_by_make_model_type_subtype_year('Test Make', 'Test Model', 'Test Type', 'Test Sub Type', 2022)
    assert retrieved_hvac_equipment_type is None


def test_delete_hvac_equipment_type_deletes_hvac_equipment_type(db_session_for_tests: Session):
    service = HvacEquipmentTypesService(
        hvac_equipment_types_repository=PostgresHvacEquipmentTypesRepository(db_session_for_tests)    
    )

    hvac_equipment_type_create = HvacEquipmentTypeCreate(
        make='Test Hvac Equipment',
        model='Test Model',
        type='Test Type',
        subtype='Test Sub Type',
        year_manufactured=2022
    )
    hvac_equipment_type = service.create_hvac_equipment_type(hvac_equipment_type_create)
    service.delete_hvac_equipment_type(hvac_equipment_type.hvac_equipment_type_id)
    hvac_equipment_type_model = service.get_hvac_equipment_type_by_id(hvac_equipment_type.hvac_equipment_type_id)
    assert hvac_equipment_type_model is None
