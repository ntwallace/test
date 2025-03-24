from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException
from fastapi.security import SecurityScopes
import pytest

from app.v1.dependencies import verify_jwt_authorization
from app.v1.schemas import AccessScope, AccessTokenData


def test_raises_when_missing_access_token():
    with pytest.raises(HTTPException):
        verify_jwt_authorization(
            security_scopes=SecurityScopes(scopes=[]),
            access_token=None,
        )

def test_authorizes_access_token_for_empty_scopes():
    try:
        verify_jwt_authorization(
            security_scopes=SecurityScopes(scopes=[]),
            access_token=AccessTokenData(
                user_id=uuid4(),
                given_name='Test',
                family_name='User',
                email='test@test.com',
                access_scopes=[],
                exp=datetime.now() + timedelta(days=1),
            ),
        )
    except HTTPException:
        assert False, 'verify_any_authorization raised HTTPException'


def test_authorizes_access_token_for_specific_scopes():
    try:
        verify_jwt_authorization(
            security_scopes=SecurityScopes(scopes=[AccessScope.ORGANIZATIONS_READ]),
            access_token=AccessTokenData(
                user_id=uuid4(),
                given_name='Test',
                family_name='User',
                email='test@test.com',
                access_scopes=[AccessScope.ORGANIZATIONS_READ],
                exp=datetime.now() + timedelta(days=1),
            ),
        )
    except HTTPException:
        assert False, 'verify_any_authorization raised HTTPException'


def test_raises_when_access_token_is_missing_scopes():
    with pytest.raises(HTTPException):
        verify_jwt_authorization(
            security_scopes=SecurityScopes(scopes=[AccessScope.ORGANIZATIONS_READ]),
            access_token=AccessTokenData(
                user_id=uuid4(),
                given_name='Test',
                family_name='User',
                email='test@test.com',
                access_scopes=[],
                exp=datetime.now() + timedelta(days=1),
            ),
        )
