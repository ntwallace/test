from datetime import datetime
from typing import List, Optional
from unittest.mock import Mock
from uuid import uuid4

from fastapi import HTTPException
from fastapi.security import SecurityScopes
import pytest

from app.v1.auth.helpers.api_key_access_scopes_helper import APIKeyAccessScopesHelper
from app.v1.auth.schemas.api_key import APIKey
from app.v1.dependencies import verify_api_key_authorization
from app.v1.schemas import AccessScope


def mock_api_keys_access_scopes_helper(scopes: Optional[List[AccessScope]] = None) -> APIKeyAccessScopesHelper:
    if scopes is None:
        scopes = []
    helper = Mock()
    helper.get_all_access_scopes_for_api_key.return_value = scopes
    return helper


def test_raises_when_missing_api_key():
    with pytest.raises(HTTPException):
        verify_api_key_authorization(
            security_scopes=SecurityScopes(scopes=[]),
            api_key=None,
            api_keys_access_scopes_helper=mock_api_keys_access_scopes_helper(),
        )


def test_authorizes_api_key_for_empty_scopes():
    try:
        verify_api_key_authorization(
            security_scopes=SecurityScopes(scopes=[]),
            api_key=APIKey(
                api_key_id=uuid4(),
                name='api key',
                api_key_hash='hash',
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            api_keys_access_scopes_helper=mock_api_keys_access_scopes_helper(),
        )
    except HTTPException:
        assert False, 'verify_any_authorization raised HTTPException'


def test_authorizes_api_key_for_specific_scopes():
    try:
        verify_api_key_authorization(
            security_scopes=SecurityScopes(scopes=[AccessScope.ORGANIZATIONS_READ]),
            api_key=APIKey(
                api_key_id=uuid4(),
                name='api key',
                api_key_hash='hash',
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            api_keys_access_scopes_helper=mock_api_keys_access_scopes_helper(
                scopes=[AccessScope.ORGANIZATIONS_READ]
            ),
        )
    except HTTPException:
        assert False, 'verify_any_authorization raised HTTPException'


def test_raises_when_api_key_is_missing_scopes():
    with pytest.raises(HTTPException):
        verify_api_key_authorization(
            security_scopes=SecurityScopes(scopes=[AccessScope.ORGANIZATIONS_READ]),
            api_key=APIKey(
                api_key_id=uuid4(),
                name='api key',
                api_key_hash='hash',
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            api_keys_access_scopes_helper=mock_api_keys_access_scopes_helper(),
        )