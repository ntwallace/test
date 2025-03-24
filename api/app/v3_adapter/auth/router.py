import logging

from uuid import UUID
from fastapi import APIRouter, Body, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.errors import NotFoundError
from app.v1.auth.helpers.user_access_scopes_helper import UserAccessScopesHelper
from app.v1.auth.routers.auth import login, refresh
from app.v1.dependencies import get_refresh_token_data, get_user_access_scopes_helper, get_users_service
from app.v1.users.services.users import UsersService
from app.v3_adapter.auth.errors import ResetCodeExiredError
from app.v3_adapter.auth.schemas import AuthSessionResponse, AuthSessionResponseData, GetResetCodeResponse, PostAuthPasswordRequest, PostAuthPasswordResponse, PostResetCodeRequest, PostResetCodeResponse, TokenRefreshRequestData, TokenRefreshResponse, TokenRefreshResponseData
from app.v3_adapter.auth.services import AuthResetCodeService
from app.v3_adapter.dependencies import get_auth_reset_codes_service


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

router = APIRouter()


@router.post('/auth/session')
def post_auth_session(
    email: str = Body(...),
    password: str = Body(...),
    users_service: UsersService = Depends(get_users_service),
    user_access_scopes_helper: UserAccessScopesHelper = Depends(get_user_access_scopes_helper),
):
    login_tokens = login(
        form_data=OAuth2PasswordRequestForm(
            username=email,
            password=password
        ),
        users_service=users_service,
        user_access_scopes_helper=user_access_scopes_helper,
    )
    return AuthSessionResponse(
        code='200',
        message='Success',
        data=AuthSessionResponseData(
            access_token=login_tokens.access_token,
            refresh_token=login_tokens.refresh_token,
            token_type=login_tokens.token_type
        )
    )

@router.post('/auth/token-refresh')
def post_auth_token_refresh(
    spec: TokenRefreshRequestData,
    users_service: UsersService = Depends(get_users_service),
    user_access_scopes_helper: UserAccessScopesHelper = Depends(get_user_access_scopes_helper),
):
    refresh_token_data = get_refresh_token_data(refresh_token=spec.refresh_token)
    access_token = refresh(
        refresh_token=refresh_token_data,
        users_service=users_service,
        user_access_scopes_helper=user_access_scopes_helper,
    )
    return TokenRefreshResponse(
        code='200',
        message='Success',
        data=TokenRefreshResponseData(
            access_token=access_token.access_token,
            refresh_token=spec.refresh_token,
            token_type=access_token.token_type
        )
    )


@router.post('/auth/logout')
def post_logout():
    return {
        'code': '200',
        'message': 'Success'
    }

@router.post(
    '/auth/reset-code',
    response_model=PostResetCodeResponse
)
def post_reset_code(
    request_spec: PostResetCodeRequest,
    users_service: UsersService = Depends(get_users_service),
    auth_reset_code_service: AuthResetCodeService = Depends(get_auth_reset_codes_service)
) -> PostResetCodeResponse:
    cleaned_email = request_spec.email.lower().strip()
    user = users_service.get_user_by_email(email=cleaned_email)
    if user is None:
        logger.warning("Trying to reset code for email that does not exist")
    else:
        logger.warning(f"Account reset password request: {user.user_id}")
        auth_reset_code_service.send_reset_password_email(user)
    return PostResetCodeResponse(
        code='200',
        message='Success',
        data=None
    )

@router.get(
    '/auth/reset-code',
    response_model=GetResetCodeResponse
)
def get_reset_code(
    email: str,
    code: UUID,
    users_service: UsersService = Depends(get_users_service),
    auth_reset_code_service: AuthResetCodeService = Depends(get_auth_reset_codes_service)
):
    cleaned_email = email.lower().strip()
    user = users_service.get_user_by_email(email=cleaned_email)
    if user is None:
        return GetResetCodeResponse(
            code='404',
            message='code_not_found',
            data=None
        )
    
    try:
        is_reset_code_valid = auth_reset_code_service.verify_reset_code(user.user_id, code)        
    except NotFoundError:
        return GetResetCodeResponse(
            code='404',
            message='code_not_found',
            data=None
        )
    except ResetCodeExiredError:
        return GetResetCodeResponse(
            code='400',
            message='code_expired',
            data=None
        )

    if not is_reset_code_valid:
        return GetResetCodeResponse(
            code='404',
            message='code_not_found',
            data=None
        )
    
    return GetResetCodeResponse(
        code='200',
        message='Success',
        data=None
    )

@router.post(
    '/auth/password',
    response_model=PostAuthPasswordResponse
)
def post_auth_password(
    request_spec: PostAuthPasswordRequest,
    users_service: UsersService = Depends(get_users_service),
    auth_reset_code_service: AuthResetCodeService = Depends(get_auth_reset_codes_service)
):
    cleaned_email = request_spec.email.lower().strip()
    user = users_service.get_user_by_email(email=cleaned_email)
    if user is None:
        return PostAuthPasswordResponse(
            code='404',
            message='code_not_found',
            data=None
        )

    try:
        is_reset_code_valid = auth_reset_code_service.verify_reset_code(user.user_id, request_spec.code)
    except NotFoundError:
        return PostAuthPasswordResponse(
            code='404',
            message='code_not_found',
            data=None
        )
    except ResetCodeExiredError:
        return PostAuthPasswordResponse(
            code='400',
            message='code_expired',
            data=None
        )
    
    if not is_reset_code_valid:
        return PostAuthPasswordResponse(
            code='404',
            message='code_not_found',
            data=None
        )
    
    users_service.update_password(user.user_id, request_spec.password)
    auth_reset_code_service.delete_reset_code(user.user_id)

    logger.warning(f'Account successful reset password: {user.user_id}')

    return PostAuthPasswordResponse(
        code='200',
        message='Success',
        data=None
    )
