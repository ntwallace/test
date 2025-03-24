from datetime import datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest

from app.v1.auth.schemas.access_role import AccessRole
from app.v1.auth.schemas.access_role_access_scope import AccessRoleAccessScope
from app.v1.schemas import AccessScope


@pytest.fixture
def mock_access_roles_service() -> Mock:
    return Mock()


@pytest.fixture
def mock_access_role_access_scopes_service() -> Mock:
    return Mock()


@pytest.fixture
def sample_access_role_id():
    return uuid4()


@pytest.fixture
def sample_access_role(sample_access_role_id) -> AccessRole:
    return AccessRole(
        access_role_id=sample_access_role_id,
        name="test:role",
        created_at=datetime(2024, 3, 12),
        updated_at=datetime(2024, 3, 12)
    )


@pytest.fixture
def sample_access_role_access_scope(sample_access_role_id) -> AccessRoleAccessScope:
    return AccessRoleAccessScope(
        access_role_id=sample_access_role_id,
        access_scope=AccessScope.ADMIN,
        created_at=datetime(2024, 3, 12)
    )
