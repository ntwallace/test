from uuid import uuid4
import pytest
from sqlalchemy.orm import Session

from app.v1.auth.repositories.api_keys_repository import PostgresAPIKeysRepository
from app.v1.auth.models.api_key import APIKey as APIKeyModel
from app.v1.auth.schemas.api_key import APIKey, APIKeyCreate


def test_create_inserts_new_model(db_session_for_tests: Session):
    api_keys_repository = PostgresAPIKeysRepository(db_session_for_tests)

    api_key_create = APIKeyCreate(
        name='Test API Key',
        api_key_hash='asdfasdf',
    )
    api_key = api_keys_repository.create(api_key_create)

    api_key_models = db_session_for_tests.query(APIKeyModel).all()
    assert len(api_key_models) == 1
    assert APIKey.model_validate(api_key_models[0], from_attributes=True) == api_key


def test_create_raises_error_if_api_key_exists(db_session_for_tests: Session):
    api_keys_repository = PostgresAPIKeysRepository(db_session_for_tests)

    api_key_create = APIKeyCreate(
        name='Test API Key',
        api_key_hash='asdfasdf',
    )
    api_keys_repository.create(api_key_create)

    with pytest.raises(ValueError):
        api_keys_repository.create(api_key_create)


def test_filter_by_returns_api_key_by_name(db_session_for_tests: Session):
    api_keys_repository = PostgresAPIKeysRepository(db_session_for_tests)

    api_key_create = APIKeyCreate(
        name='Test API Key',
        api_key_hash='asdfasdf',
    )
    api_key = api_keys_repository.create(api_key_create)

    other_api_key_create = APIKeyCreate(
        name='Other API Key',
        api_key_hash='asdfasdf2',
    )
    api_keys_repository.create(other_api_key_create)

    api_keys = api_keys_repository.filter_by(name='Test API Key')
    assert len(api_keys) == 1
    assert api_keys[0] == api_key


def test_filter_by_returns_api_key_by_api_key_hash(db_session_for_tests: Session):
    api_keys_repository = PostgresAPIKeysRepository(db_session_for_tests)

    api_key_create = APIKeyCreate(
        name='Test API Key',
        api_key_hash='asdfasdf',
    )
    api_key = api_keys_repository.create(api_key_create)

    other_api_key_create = APIKeyCreate(
        name='Other API Key',
        api_key_hash='asdfasdf2',
    )
    api_keys_repository.create(other_api_key_create)

    api_keys = api_keys_repository.filter_by(api_key_hash='asdfasdf')
    assert len(api_keys) == 1
    assert api_keys[0] == api_key


def test_filter_by_returns_empty_list_when_no_api_key_exists(db_session_for_tests: Session):
    api_keys_repository = PostgresAPIKeysRepository(db_session_for_tests)

    api_key_create = APIKeyCreate(
        name='Test API Key',
        api_key_hash='asdfasdf',
    )
    api_key = api_keys_repository.create(api_key_create)

    api_keys = api_keys_repository.filter_by(name='asdfasdf')
    assert len(api_keys) == 0


def test_get_returns_api_key(db_session_for_tests: Session):
    api_keys_repository = PostgresAPIKeysRepository(db_session_for_tests)

    api_key_create = APIKeyCreate(
        name='Test API Key',
        api_key_hash='asdfasdf',
    )
    api_key = api_keys_repository.create(api_key_create)

    retreived_api_key = api_keys_repository.get(api_key.api_key_id)
    assert retreived_api_key == api_key


def test_get_returns_none_when_api_key_does_not_exist(db_session_for_tests: Session):
    api_keys_repository = PostgresAPIKeysRepository(db_session_for_tests)

    api_key = api_keys_repository.get(uuid4())
    assert api_key is None


def test_delete_removes_api_key(db_session_for_tests: Session):
    api_keys_repository = PostgresAPIKeysRepository(db_session_for_tests)

    api_key_create = APIKeyCreate(
        name='Test API Key',
        api_key_hash='asdfasdf',
    )
    api_key = api_keys_repository.create(api_key_create)

    api_keys_repository.delete(api_key.api_key_id)

    api_key = api_keys_repository.get(api_key.api_key_id)
    assert api_key is None
