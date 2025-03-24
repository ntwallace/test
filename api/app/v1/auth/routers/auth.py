import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.v1.auth.helpers.user_access_scopes_helper import UserAccessScopesHelper
from app.v1.auth.schemas.login_tokens import LoginTokens
from app.v1.schemas import AccessScope, AccessToken, RefreshTokenData
from app.v1.auth.utils import generate_access_token_for_user, generate_refresh_token_for_user
from app.v1.dependencies import (
    get_refresh_token_data,
    get_user_access_scopes_helper,
    get_users_service
)
from app.v1.users.services.users import UsersService
from app.v1.utils import verify_password


ENVIRONMENT = os.environ.get('ENVIRONMENT', 'production')


router = APIRouter()


@router.post('/login', response_model=LoginTokens)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    users_service: UsersService = Depends(get_users_service),
    user_access_scopes_helper: UserAccessScopesHelper = Depends(get_user_access_scopes_helper)
) -> LoginTokens:
    user = users_service.get_user_by_email(email=form_data.username)
    if not user:
        raise HTTPException(status_code=404, detail='not_found')
    
    if user.password_hash is None:
        raise HTTPException(status_code=404, detail='not_found')

    password_verified = verify_password(form_data.password, user.password_hash)
    if not password_verified:
        raise HTTPException(status_code=404, detail='not_found')
    
    use_scopes = None
    if ENVIRONMENT != 'production' and len(form_data.scopes) > 0:
        use_scopes = [AccessScope(scope) for scope in form_data.scopes]

    encoded_access_token = generate_access_token_for_user(
        user=user,
        user_access_scopes_helper=user_access_scopes_helper,
        use_scopes=use_scopes,
    )

    encoded_refresh_token = generate_refresh_token_for_user(
        user=user
    )
    
    return LoginTokens(
        access_token=encoded_access_token,
        refresh_token=encoded_refresh_token,
        token_type='bearer'
    )


@router.post('/refresh', response_model=AccessToken)
def refresh(
    refresh_token: RefreshTokenData = Depends(get_refresh_token_data),
    users_service: UsersService = Depends(get_users_service),
    user_access_scopes_helper: UserAccessScopesHelper = Depends(get_user_access_scopes_helper)
) -> AccessToken:
    user = users_service.get_user_by_user_id(refresh_token.user_id)
    if not user:
        raise HTTPException(status_code=400, detail='Invalid token')

    encoded_access_token = generate_access_token_for_user(
        user=user,
        user_access_scopes_helper=user_access_scopes_helper
    )
    return AccessToken(
        access_token=encoded_access_token,
        token_type='bearer'
    ) 