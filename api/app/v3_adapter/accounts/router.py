from fastapi import APIRouter, Depends, HTTPException

from app.v1.dependencies import get_access_token_data, get_users_service
from app.v1.schemas import AccessTokenData
from app.v1.users.schemas.user import UserUpdate
from app.v1.users.services.users import UsersService
from app.v3_adapter.accounts.schemas import GetMyAccountResponse, GetMyAccountResponseData, PatchMyAccountRequest, PatchMyAccountResponse, PatchMyAccountResponseData


router = APIRouter()


@router.get(
    '/accounts/me',
    dependencies=[Depends(get_access_token_data)],
    response_model=GetMyAccountResponse
)
def get_my_account(
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    users_service: UsersService = Depends(get_users_service),
):
    user = users_service.get_user_by_user_id(access_token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    return GetMyAccountResponse(
        data=GetMyAccountResponseData(
            id=user.user_id,
            given_name=user.first_name,
            family_name=user.last_name,
            email=user.email,
            phone_number=user.phone_number
        ),
        message='200',
        code='success'
    )


@router.patch(
    '/accounts/me',
    dependencies=[Depends(get_access_token_data)],
    response_model=PatchMyAccountResponse
)
def patch_my_account(
    patch_my_account_request: PatchMyAccountRequest,
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    users_service: UsersService = Depends(get_users_service),
):
    user = users_service.get_user_by_user_id(access_token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    user = users_service.update_user(
        UserUpdate(
            user_id=user.user_id,
            first_name=patch_my_account_request.given_name.new_value if patch_my_account_request.given_name else user.first_name,
            last_name=patch_my_account_request.family_name.new_value if patch_my_account_request.family_name else user.last_name,
            phone_number=patch_my_account_request.phone_number.new_value if patch_my_account_request.phone_number else user.phone_number
        )
    )
    
    return PatchMyAccountResponse(
        data=PatchMyAccountResponseData(
            id=user.user_id,
            given_name=user.first_name,
            family_name=user.last_name,
            email=user.email,
            phone_number=user.phone_number
        ),
        message='200',
        code='success'
    )
