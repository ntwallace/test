from datetime import datetime, timedelta
from uuid import uuid4, UUID

from fastapi import HTTPException
import pytest
from jwt import PyJWTError

from app.v1.auth.utils import encode_access_token, encode_refresh_token
from app.v1.dependencies import get_refresh_token_data
from app.v1.schemas import AccessScope, AccessTokenData, RefreshTokenData


def test_get_refresh_token_data_successfully_decodes_refresh_token():
    refresh_token_data = RefreshTokenData(
        user_id=uuid4(),
        exp=datetime.now() + timedelta(minutes=15)
    )
    encoded_refresh_token = encode_refresh_token(
        token_data=refresh_token_data
    )
    decoded_refresh_token = get_refresh_token_data(encoded_refresh_token)
    assert decoded_refresh_token.user_id == refresh_token_data.user_id


def test_get_refresh_token_data_when_decoding_access_token():
    access_token_data = AccessTokenData(
        user_id=uuid4(),
        given_name='Lando',
        family_name='Norris',
        email='lando@powerx.co',
        access_scopes=[AccessScope.ADMIN],
        organization_ids=[uuid4()],
        location_ids=[uuid4()],
        exp=datetime.now() + timedelta(minutes=15)
    )
    encoded_access_token = encode_access_token(
        token_data=access_token_data
    )
    with pytest.raises(HTTPException):
        get_refresh_token_data(encoded_access_token)
