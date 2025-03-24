from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Security, status, Query
from uuid import UUID

from app.v1.dependencies import get_access_token_data, get_access_token_data_or_raise, get_users_service, verify_any_authorization, verify_jwt_authorization
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.users.services.users import UsersService
from app.v1.users.schemas.user import UserCreate, UserRead


router = APIRouter(tags=['users'])


def _authorize_token_for_user_access(
    user_id: UUID,
    token_data: Annotated[AccessTokenData, Depends(get_access_token_data_or_raise)]
) -> UUID:
    if AccessScope.ADMIN in token_data.access_scopes:
        return user_id
    if user_id != token_data.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    return user_id


@router.post('/',
             dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.USERS_WRITE])],
             response_model=UserRead,
             status_code=201)
def create_user(user: UserCreate,
                users_service: UsersService = Depends(get_users_service)):
    user_check = users_service.get_user_by_email(user.email)
    if user_check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')
    user_schema = users_service.create_user(user)
    return user_schema


@router.get('/{user_id}',
            dependencies=[Security(verify_any_authorization, scopes=[AccessScope.USERS_READ])],
            response_model=UserRead)
def get_user(user_id: UUID,
             access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
             users_service: UsersService = Depends(get_users_service)):
    if access_token_data is not None:
        _authorize_token_for_user_access(
            user_id=user_id,
            token_data=access_token_data
        )

    user = users_service.get_user_by_user_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user


@router.get('/',
            dependencies=[Security(verify_any_authorization, scopes=[AccessScope.USERS_READ])],
            response_model=List[UserRead])
def list_users(
    email: Optional[str] = Query(None, description="Filter users by exact email match"),
    email_like: Optional[str] = Query(None, description="Filter users by email pattern"),
    users_service: UsersService = Depends(get_users_service)
):
    if email is not None and email_like is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot use both 'email' and 'email_like' parameters together"
        )
    
    if email is not None:
        user = users_service.get_user_by_email(email)
        return [user] if user else []
    if email_like is not None:
        return users_service.get_users_by_email_pattern(email_like)
    return users_service.get_all_users()
