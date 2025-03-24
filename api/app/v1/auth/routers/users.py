from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status

from app.v1.auth.helpers.user_access_scopes_helper import UserAccessScopesHelper
from app.v1.auth.schemas.user_access_role import PostUserAccessRoleRequest, UserAccessRole, UserAccessRoleCreate
from app.v1.auth.services.access_roles import AccessRolesService
from app.v1.auth.services.user_access_roles import UserAccessRolesService
from app.v1.auth.services.user_access_scopes import UserAccessScopesService
from app.v1.dependencies import (
    get_access_roles_service,
    get_user_access_roles_service,
    get_user_access_scopes_helper,
    get_user_access_scopes_service,
    get_users_service,
    verify_jwt_authorization
)
from app.v1.schemas import AccessScope
from app.v1.users.services.users import UsersService


router = APIRouter()


@router.post(
    "/{user_id}/access-roles",
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN])],
    response_model=UserAccessRole,
    status_code=status.HTTP_201_CREATED
)
def associate_access_role_with_user(
    user_id: UUID,
    request: PostUserAccessRoleRequest,
    users_service: UsersService = Depends(get_users_service),
    access_roles_service: AccessRolesService = Depends(get_access_roles_service),
    user_access_roles_service: UserAccessRolesService = Depends(get_user_access_roles_service)
) -> UserAccessRole:
    user = users_service.get_user_by_user_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    access_role = access_roles_service.get_access_role(request.access_role_id)
    if access_role is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid access role')
    
    return user_access_roles_service.create_user_access_role(
        UserAccessRoleCreate(
            user_id=user_id,
            access_role_id=request.access_role_id
        )
    )


@router.delete(
    "/{user_id}/access-roles/{access_role_id}",
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN])],
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_access_role_from_user(
    user_id: UUID,
    access_role_id: UUID,
    users_service: UsersService = Depends(get_users_service),
    access_roles_service: AccessRolesService = Depends(get_access_roles_service),
    user_access_roles_service: UserAccessRolesService = Depends(get_user_access_roles_service)
) -> None:
    user = users_service.get_user_by_user_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    access_role = access_roles_service.get_access_role(access_role_id)
    if access_role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Access role not found')

    user_access_roles_service.delete_user_access_role(user_id, access_role_id)


@router.get(
    "/{user_id}/access-roles",
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN])],
    response_model=List[UserAccessRole]
)
def list_user_access_roles(
    user_id: UUID,
    users_service: UsersService = Depends(get_users_service),
    user_access_roles_service: UserAccessRolesService = Depends(get_user_access_roles_service)
) -> List[UserAccessRole]:
    user = users_service.get_user_by_user_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    return user_access_roles_service.get_user_access_roles(user_id)


@router.put(
    "/{user_id}/access-scopes",
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN])],
    response_model=List[AccessScope]
)
def update_user_access_scopes(
    user_id: UUID,
    access_scopes: List[AccessScope],
    users_service: UsersService = Depends(get_users_service),
    user_access_scopes_service: UserAccessScopesService = Depends(get_user_access_scopes_service)
) -> List[AccessScope]:
    user = users_service.get_user_by_user_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    return user_access_scopes_service.update_user_access_scopes(user_id, access_scopes)


@router.get(
    "/{user_id}/access-scopes",
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN])],
    response_model=List[AccessScope]
)
def list_user_access_scopes(
    user_id: UUID,
    users_service: UsersService = Depends(get_users_service),
    user_access_scopes_service: UserAccessScopesService = Depends(get_user_access_scopes_service)
) -> List[AccessScope]:
    user = users_service.get_user_by_user_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    return user_access_scopes_service.get_access_scopes_for_user(user_id)


@router.get(
    "/{user_id}/effective-access-scopes",
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN])],
    response_model=List[AccessScope]
)
def list_user_effective_access_scopes(
    user_id: UUID,
    users_service: UsersService = Depends(get_users_service),
    user_access_scopes_helper: UserAccessScopesHelper = Depends(get_user_access_scopes_helper)
) -> List[AccessScope]:
    user = users_service.get_user_by_user_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    
    return user_access_scopes_helper.get_all_access_scopes_for_user(user_id) 