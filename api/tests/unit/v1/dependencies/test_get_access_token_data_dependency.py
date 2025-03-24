from datetime import datetime, timedelta
from uuid import uuid4, UUID

from fastapi import HTTPException
import pytest
from jwt import PyJWTError

from app.v1.auth.utils import encode_access_token, encode_refresh_token
from app.v1.dependencies import get_access_token_data
from app.v1.schemas import AccessScope, AccessTokenData, RefreshTokenData


def test_get_access_token_data_successfully_decodes_access_token():
    access_token_data = AccessTokenData(
        user_id=uuid4(),
        given_name='John',
        family_name='Doe',
        email='jon@doe.com',
        access_scopes=[AccessScope.ADMIN],
        exp=datetime.now() + timedelta(minutes=15)
    )
    encoded_access_token = encode_access_token(
        token_data=access_token_data
    )
    decoded_access_token = get_access_token_data(encoded_access_token)
    assert decoded_access_token.user_id == access_token_data.user_id
    assert decoded_access_token.access_scopes == access_token_data.access_scopes


def test_get_refresh_token_data_when_decoding_access_token():
    refresh_token_data = RefreshTokenData(
        user_id=uuid4(),
        exp=datetime.now() + timedelta(minutes=15)
    )
    encoded_refresh_token = encode_refresh_token(
        token_data=refresh_token_data
    )
    access_token_data = get_access_token_data(encoded_refresh_token)
    assert access_token_data is None
