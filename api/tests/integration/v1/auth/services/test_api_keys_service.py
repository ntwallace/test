from datetime import datetime
from uuid import UUID
import pytest

from sqlalchemy.orm import Session

from app.v1.auth.repositories.api_keys_repository import PostgresAPIKeysRepository
from app.v1.auth.schemas.api_key import APIKey
from app.v1.auth.services.api_keys import APIKeysService


@pytest.fixture
def api_keys_service(db_session_for_tests: Session):
    return APIKeysService(
        api_keys_repository=PostgresAPIKeysRepository(db_session_for_tests)
    )

def test_create_new_api_key_returns_api_key_string_and_api_key_object(
    api_keys_service: APIKeysService,
):
    (api_key_string, api_key) = api_keys_service.create_api_key(name='test')

    assert isinstance(api_key_string, str)
    assert isinstance(api_key, APIKey)
    assert isinstance(api_key.api_key_id, UUID)
    assert api_key.name == 'test'
    assert isinstance(api_key.api_key_hash, str)
    assert isinstance(api_key.created_at, datetime)
    assert isinstance(api_key.updated_at, datetime)


def test_cerate_new_api_key_when_api_key_exists(
    api_keys_service: APIKeysService
):
    api_keys_service.create_api_key(name='test')

    with pytest.raises(ValueError):
        api_keys_service.create_api_key(name='test')
