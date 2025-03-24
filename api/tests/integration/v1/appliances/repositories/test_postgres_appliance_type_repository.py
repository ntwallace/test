from typing import List
from uuid import uuid4, UUID
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.appliances.models.appliance_type import ApplianceType
from app.v1.appliances.repositories.appliance_types_repository import PostgresApplianceTypesRepository
from app.v1.appliances.schemas.appliance_type import ApplianceTypeCreate


def test_create_inserts_new_model(db_session_for_tests: Session):
    appliance_types_repository = PostgresApplianceTypesRepository(db_session_for_tests)

    appliance_type_create = ApplianceTypeCreate(make='Test Appliance', model='Test Model', type='Test Type', sub_type='Test Sub Type', year_manufactured=2022)
    appliance_type = appliance_types_repository.create(appliance_type_create)

    appliance_type_models = db_session_for_tests.query(ApplianceType).all()
    assert len(appliance_type_models) == 1
    appliance_type_model = appliance_type_models[0]
    assert appliance_type_model.make == appliance_type.make
    assert appliance_type_model.model == appliance_type.model
    assert appliance_type_model.type == appliance_type.type
    assert appliance_type_model.subtype == appliance_type.subtype
    assert appliance_type_model.year_manufactured == appliance_type.year_manufactured
    assert appliance_type_model.appliance_type_id == appliance_type.appliance_type_id
    assert appliance_type_model.created_at == appliance_type.created_at
    assert appliance_type_model.updated_at == appliance_type.updated_at


def test_create_inserts_new_model_nulls(db_session_for_tests: Session):
    appliance_types_repository = PostgresApplianceTypesRepository(db_session_for_tests)
    
    appliance_type_create = ApplianceTypeCreate(make='Test Appliance 2', type='Test Type 2')
    appliance_type = appliance_types_repository.create(appliance_type_create)

    appliance_type_models = db_session_for_tests.query(ApplianceType).all()
    assert len(appliance_type_models) == 1
    appliance_type_model = appliance_type_models[0]
    assert appliance_type_model.make == appliance_type.make
    assert appliance_type_model.model is None
    assert appliance_type_model.type == appliance_type.type
    assert appliance_type_model.subtype is None
    assert appliance_type_model.year_manufactured is None
    assert appliance_type_model.appliance_type_id == appliance_type.appliance_type_id
    assert appliance_type_model.created_at == appliance_type.created_at
    assert appliance_type_model.updated_at == appliance_type.updated_at


def test_create_raises_error_if_appliance_type_exists(db_session_for_tests: Session):
    appliance_types_repository = PostgresApplianceTypesRepository(db_session_for_tests)
    
    appliance_type_create = ApplianceTypeCreate(make='Test Appliance', model='Test Model', type='Test Type', subtype='Test Sub Type', year_manufactured=2022)
    appliance_types_repository.create(appliance_type_create)

    with pytest.raises(IntegrityError):
        appliance_types_repository.create(appliance_type_create)


def test_get_returns_appliance_type(db_session_for_tests: Session):
    appliance_types_repository = PostgresApplianceTypesRepository(db_session_for_tests)
    
    appliance_type_create = ApplianceTypeCreate(make='Test Appliance', model='Test Model', type='Test Type', sub_type='Test Sub Type', year_manufactured=2022)
    appliance_type = appliance_types_repository.create(appliance_type_create)

    retrieved_appliance_type = appliance_types_repository.get(appliance_type.appliance_type_id)
    assert retrieved_appliance_type.make == appliance_type.make
    assert retrieved_appliance_type.model == appliance_type.model
    assert retrieved_appliance_type.type == appliance_type.type
    assert retrieved_appliance_type.subtype == appliance_type.subtype
    assert retrieved_appliance_type.year_manufactured == appliance_type.year_manufactured
    assert retrieved_appliance_type.appliance_type_id == appliance_type.appliance_type_id
    assert retrieved_appliance_type.created_at == appliance_type.created_at
    assert retrieved_appliance_type.updated_at == appliance_type.updated_at


def test_get_returns_none_if_appliance_type_does_not_exist(db_session_for_tests: Session):
    appliance_types_repository = PostgresApplianceTypesRepository(db_session_for_tests)
    
    retrieved_appliance_type = appliance_types_repository.get(uuid4())
    assert retrieved_appliance_type is None


def test_filter_by_returns_appliance_types(db_session_for_tests: Session):
    appliance_types_repository = PostgresApplianceTypesRepository(db_session_for_tests)
    
    appliance_type_create = ApplianceTypeCreate(make='Test Appliance', model='Test Model', type='Test Type', subtype='Test Sub Type', year_manufactured=2022)
    appliance_type = appliance_types_repository.create(appliance_type_create)

    retrieved_appliance_types: List[ApplianceType] = appliance_types_repository.filter_by(
        make=appliance_type_create.make,
        model=appliance_type_create.model,
        type=appliance_type_create.type,
        subtype=appliance_type_create.subtype,
        year_manufactured=appliance_type_create.year_manufactured
    )
    assert len(retrieved_appliance_types) == 1
    retrieved_appliance_type = retrieved_appliance_types[0]
    assert retrieved_appliance_type.make == appliance_type.make
    assert retrieved_appliance_type.model == appliance_type.model
    assert retrieved_appliance_type.type == appliance_type.type
    assert retrieved_appliance_type.subtype == appliance_type.subtype
    assert retrieved_appliance_type.year_manufactured == appliance_type.year_manufactured
    assert retrieved_appliance_type.appliance_type_id == appliance_type.appliance_type_id
    assert retrieved_appliance_type.created_at == appliance_type.created_at
    assert retrieved_appliance_type.updated_at == appliance_type.updated_at


def test_filter_by_returns_empty_list_if_none_exist(db_session_for_tests: Session):
    appliance_types_repository = PostgresApplianceTypesRepository(db_session_for_tests)
    
    retrieved_appliance_type = appliance_types_repository.filter_by(
        make='Test Appliance',
        model='Test Model',
        type='Test Type',
        subtype='Test Sub Type',
        year_manufactured=2022
    )
    assert len(retrieved_appliance_type) == 0


def test_delete_appliance_type_deletes_appliance_type(db_session_for_tests: Session):
    appliance_types_repository = PostgresApplianceTypesRepository(db_session_for_tests)
    
    appliance_type_create = ApplianceTypeCreate(make='Test Appliance', model='Test Model', type='Test Type', subtype='Test Sub Type', year_manufactured=2022)
    appliance_type = appliance_types_repository.create(appliance_type_create)
    appliance_types_repository.delete(appliance_type.appliance_type_id)
    appliance_type_model = appliance_types_repository.get(appliance_type.appliance_type_id)
    assert appliance_type_model is None
