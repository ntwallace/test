from typing import List
from uuid import uuid4, UUID
import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.appliances.models.appliance import Appliance
from app.v1.appliances.repositories.appliances_repository import PostgresAppliancesRepository
from app.v1.appliances.schemas.appliance import ApplianceCreate
from app.v1.appliances.schemas.appliance_type import ApplianceSuperTypeEnum


def test_create_inserts_new_model(db_session_for_tests: Session):
    appliances_repository = PostgresAppliancesRepository(db_session_for_tests)

    appliance_create = ApplianceCreate(name='test appliance', appliance_super_type=ApplianceSuperTypeEnum.FRIDGE, appliance_type_id=uuid4(), location_id=uuid4(), circuit_id=uuid4(), temperature_sensor_place_id=uuid4(), serial='Test Serial')
    appliance = appliances_repository.create(appliance_create)

    appliance_models = db_session_for_tests.query(Appliance).all()
    assert len(appliance_models) == 1
    appliance_model = appliance_models[0]
    assert appliance_model.name == appliance.name
    assert appliance_model.appliance_super_type == appliance.appliance_super_type
    assert appliance_model.appliance_type_id == appliance.appliance_type_id
    assert appliance_model.location_id == appliance.location_id
    assert appliance_model.circuit_id == appliance.circuit_id
    assert appliance_model.temperature_sensor_place_id == appliance.temperature_sensor_place_id
    assert appliance_model.serial == appliance.serial
    assert appliance_model.appliance_id == appliance.appliance_id
    assert appliance_model.created_at == appliance.created_at
    assert appliance_model.updated_at == appliance.updated_at


def test_create_inserts_new_model_nulls(db_session_for_tests: Session):
    appliances_repository = PostgresAppliancesRepository(db_session_for_tests)

    appliance_create = ApplianceCreate(name='test appliance', appliance_super_type=ApplianceSuperTypeEnum.FRIDGE, appliance_type_id=uuid4(), location_id=uuid4(), circuit_id=uuid4())
    appliance = appliances_repository.create(appliance_create)

    appliance_models = db_session_for_tests.query(Appliance).all()
    assert len(appliance_models) == 1
    appliance_model = appliance_models[0]
    assert appliance_model.name == appliance.name
    assert appliance_model.appliance_super_type == appliance.appliance_super_type
    assert appliance_model.appliance_type_id == appliance.appliance_type_id
    assert appliance_model.location_id == appliance.location_id
    assert appliance_model.circuit_id == appliance.circuit_id
    assert appliance_model.temperature_sensor_place_id is None
    assert appliance_model.serial is None
    assert appliance_model.appliance_id == appliance.appliance_id
    assert appliance_model.created_at == appliance.created_at
    assert appliance_model.updated_at == appliance.updated_at


def test_create_raises_error_if_appliance_exists(db_session_for_tests: Session):
    appliances_repository = PostgresAppliancesRepository(db_session_for_tests)

    appliance_create = ApplianceCreate(name='test appliance', appliance_super_type=ApplianceSuperTypeEnum.FRIDGE, appliance_type_id=uuid4(), location_id=uuid4(), circuit_id=uuid4(), temperature_sensor_place_id=uuid4(), serial='Test Serial')
    appliances_repository.create(appliance_create)

    with pytest.raises(IntegrityError):
        appliances_repository.create(appliance_create)


def test_get_returns_appliance(db_session_for_tests: Session):
    appliances_repository = PostgresAppliancesRepository(db_session_for_tests)

    appliance_create = ApplianceCreate(name='test appliance', appliance_super_type=ApplianceSuperTypeEnum.FRIDGE, appliance_type_id=uuid4(), location_id=uuid4(), circuit_id=uuid4(), temperature_sensor_place_id=uuid4(), serial='Test Serial')
    appliance = appliances_repository.create(appliance_create)

    retrieved_appliance = appliances_repository.get(appliance.appliance_id)
    assert retrieved_appliance.name == appliance.name
    assert retrieved_appliance.appliance_super_type == appliance.appliance_super_type
    assert retrieved_appliance.appliance_type_id == appliance.appliance_type_id
    assert retrieved_appliance.location_id == appliance.location_id
    assert retrieved_appliance.circuit_id == appliance.circuit_id
    assert retrieved_appliance.temperature_sensor_place_id == appliance.temperature_sensor_place_id
    assert retrieved_appliance.serial == appliance.serial
    assert retrieved_appliance.appliance_id == appliance.appliance_id
    assert retrieved_appliance.created_at == appliance.created_at
    assert retrieved_appliance.updated_at == appliance.updated_at


def test_get_returns_none_if_appliance_does_not_exist(db_session_for_tests: Session):
    appliances_repository = PostgresAppliancesRepository(db_session_for_tests)

    retrieved_appliance_type = appliances_repository.get(uuid4())
    assert retrieved_appliance_type is None


def test_filter_by_returns_appliances(db_session_for_tests: Session):
    appliances_repository = PostgresAppliancesRepository(db_session_for_tests)

    appliance_create = ApplianceCreate(name='test appliance',
                                       appliance_super_type=ApplianceSuperTypeEnum.FRIDGE,
                                       appliance_type_id=uuid4(),
                                       location_id=uuid4(),
                                       circuit_id=uuid4(),
                                       temperature_sensor_place_id=uuid4(),
                                       serial='Test Serial')
    appliance = appliances_repository.create(appliance_create)

    retrieved_appliances: List[Appliance] = appliances_repository.filter_by(
        appliance_type_id=appliance.appliance_type_id,
        location_id=appliance.location_id,
        circuit_id=appliance.circuit_id,
        temperature_sensor_place_id=appliance.temperature_sensor_place_id,
        serial=appliance.serial
    )
    assert len(retrieved_appliances) == 1
    retrieved_appliance = retrieved_appliances[0]
    assert retrieved_appliance.name == appliance.name
    assert retrieved_appliance.appliance_super_type == appliance.appliance_super_type
    assert retrieved_appliance.appliance_type_id == appliance.appliance_type_id
    assert retrieved_appliance.location_id == appliance.location_id
    assert retrieved_appliance.circuit_id == appliance.circuit_id
    assert retrieved_appliance.temperature_sensor_place_id == appliance.temperature_sensor_place_id
    assert retrieved_appliance.serial == appliance.serial
    assert retrieved_appliance.appliance_id == appliance.appliance_id
    assert retrieved_appliance.created_at == appliance.created_at
    assert retrieved_appliance.updated_at == appliance.updated_at


def test_filter_by_returns_empty_list_if_not_exists(db_session_for_tests: Session):
    appliances_repository = PostgresAppliancesRepository(db_session_for_tests)

    retrieved_appliances = appliances_repository.filter_by(
        appliance_type_id=uuid4(),
        location_id=uuid4(),
        circuit_id=uuid4(),
        temperature_sensor_place_id=uuid4(),
        serial='Test Serial'
    )
    assert len(retrieved_appliances) == 0


def test_filter_by_using_location_id_returns_correct_appliances(db_session_for_tests: Session):
    appliances_repository = PostgresAppliancesRepository(db_session_for_tests)

    location_id = uuid4()
    appliance_type_ids = [uuid4() for _ in range(3)]
    for appliance_type_id in appliance_type_ids:
        appliance_create = ApplianceCreate(name='test appliance',
                                           appliance_super_type=ApplianceSuperTypeEnum.FRIDGE,
                                           appliance_type_id=appliance_type_id,
                                           location_id=location_id,
                                           circuit_id=uuid4(),
                                           temperature_sensor_place_id=uuid4(),
                                           serial=f'Test Serial {appliance_type_id}')
        appliances_repository.create(appliance_create)

    other_location_id = uuid4()
    other_appliance_type_id = uuid4()
    other_appliance_create = ApplianceCreate(name='test appliance',
                                             appliance_super_type=ApplianceSuperTypeEnum.FRIDGE,
                                             appliance_type_id=other_appliance_type_id,
                                             location_id=other_location_id,
                                             circuit_id=uuid4(),
                                             temperature_sensor_place_id=uuid4(),
                                             serial='Test Serial')
    appliances_repository.create(other_appliance_create)

    appliances = appliances_repository.filter_by(location_id=location_id)
    assert len(appliances) == 3
    for appliance in appliances:
        assert appliance.location_id == location_id
        assert appliance.appliance_type_id in appliance_type_ids


def test_delete(db_session_for_tests: Session):
    appliances_repository = PostgresAppliancesRepository(db_session_for_tests)

    appliance_create = ApplianceCreate(name='test appliance', appliance_super_type=ApplianceSuperTypeEnum.FRIDGE, appliance_type_id=uuid4(), location_id=uuid4(), circuit_id=uuid4(), temperature_sensor_place_id=uuid4(), serial='Test Serial')
    appliance = appliances_repository.create(appliance_create)

    appliances_repository.delete(appliance.appliance_id)

    appliance_model = appliances_repository.get(appliance.appliance_id)
    assert appliance_model is None
