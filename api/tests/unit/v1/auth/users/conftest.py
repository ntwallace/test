from datetime import datetime
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest

from app.v1.auth.schemas.access_role import AccessRole
from app.v1.auth.schemas.user_access_role import UserAccessRole
from app.v1.schemas import AccessScope
from app.v1.users.schemas.user import User


@pytest.fixture
def mock_users_service() -> Mock:
    return Mock()


@pytest.fixture
def mock_access_roles_service() -> Mock:
    return Mock()


@pytest.fixture
def mock_user_access_roles_service() -> Mock:
    return Mock()


@pytest.fixture
def mock_user_access_scopes_service() -> Mock:
    return Mock()


@pytest.fixture
def mock_user_access_scopes_helper() -> Mock:
    return Mock()


@pytest.fixture
def sample_user_id():
    return uuid4()


@pytest.fixture
def sample_access_role_id():
    return uuid4()


@pytest.fixture
def sample_user(sample_user_id: UUID):
    return User(
        user_id=sample_user_id,
        email='test@example.com',
        first_name='Test',
        last_name='User',
        created_at=datetime(2024, 3, 12),
        updated_at=datetime(2024, 3, 12)
    )

@pytest.fixture
def sample_access_role(sample_access_role_id: UUID):
    return AccessRole(
        access_role_id=sample_access_role_id,
        name='test:role',
        created_at=datetime(2024, 3, 12),
        updated_at=datetime(2024, 3, 12)
    )

@pytest.fixture
def sample_user_access_role(sample_user_id, sample_access_role_id) -> UserAccessRole:
    return UserAccessRole(
        user_id=sample_user_id,
        access_role_id=sample_access_role_id,
        created_at=datetime(2024, 3, 12)
    ) 