import os

from datetime import datetime, timedelta, timezone
from typing import List

import jwt

from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder

from app.px.pxlogger import PxLogger
from app.v1.auth.helpers.user_access_scopes_helper import UserAccessScopesHelper
from app.v1.schemas import AccessScope, RefreshTokenData, AccessTokenData
from app.v1.users.schemas.user import User


logger = PxLogger(__name__)

load_dotenv()

ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')

JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_ACCESS_TOKEN_SECRET_KEY = os.environ['JWT_ACCESS_TOKEN_SECRET_KEY']
JWT_REFRESH_TOKEN_SECRET_KEY = os.environ['JWT_REFRESH_TOKEN_SECRET_KEY']
JWT_ACCESS_TOKEN_EXPIRES_MINUTES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_MINUTES', 1440))
JWT_REFRESH_TOKEN_EXPIRES_MINUTES = int(os.environ.get('JWT_REFRESH_TOKEN_EXPIRES_MINUTES', 1440))


def encode_token(
    token_data: AccessTokenData | RefreshTokenData,
    secret_key: str
) -> str:
    encodable_token = jsonable_encoder(token_data)
    encodable_token.update({
        'exp': token_data.exp,
        'sub': str(token_data.user_id)
    })
    encoded_token = jwt.encode(encodable_token, secret_key, algorithm=JWT_ALGORITHM)
    return encoded_token

def encode_access_token(
    token_data: AccessTokenData
) -> str:
    return encode_token(token_data, JWT_ACCESS_TOKEN_SECRET_KEY)

def encode_refresh_token(
    token_data: RefreshTokenData
) -> str:
    return encode_token(token_data, JWT_REFRESH_TOKEN_SECRET_KEY)


def generate_access_token_for_user(
    user: User,
    user_access_scopes_helper: UserAccessScopesHelper,
    use_scopes: List[AccessScope] | None = None
) -> str:
    scopes_for_user: List[AccessScope] = []
    if use_scopes is not None and ENVIRONMENT != 'production':
        logger.debug('Using custom scopes')
        scopes_for_user = use_scopes
    else:
        scopes_for_user = user_access_scopes_helper.get_all_access_scopes_for_user(user.user_id)

    access_token_data = AccessTokenData(
        user_id=user.user_id,
        given_name=user.first_name,
        family_name=user.last_name,
        email=user.email,
        access_scopes=scopes_for_user,
        exp=datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRES_MINUTES)

    )
    logger.debug(f'TokenData: {access_token_data}')

    return encode_access_token(access_token_data)

def generate_refresh_token_for_user(
    user: User,
) -> str:
    refresh_token_data = RefreshTokenData(
        user_id=user.user_id,
        exp=datetime.now(timezone.utc) + timedelta(minutes=JWT_REFRESH_TOKEN_EXPIRES_MINUTES)
    )
    logger.debug(f'RefreshTokenData: {refresh_token_data}')

    return encode_refresh_token(refresh_token_data)
