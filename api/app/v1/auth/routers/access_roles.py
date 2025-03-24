from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Security, status

from app.v1.auth.schemas.access_role import AccessRole, AccessRoleCreate
from app.v1.auth.services.access_roles import AccessRolesService
from app.v1.auth.services.access_role_access_scopes import AccessRoleAccessScopesService
from app.v1.dependencies import (
    get_access_roles_service,
    get_access_role_access_scopes_service,
    verify_jwt_authorization
)
from app.v1.schemas import AccessScope


router = APIRouter()


@router.get(
    "/",
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN])],
    response_model=List[AccessRole]
)
def list_access_roles(
    access_roles_service: AccessRolesService = Depends(get_access_roles_service)
) -> List[AccessRole]:
    return access_roles_service.get_acess_roles()


@router.post(
    "/",
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN])],
    response_model=AccessRole,
    status_code=status.HTTP_201_CREATED
)
def create_access_role(
    access_role: AccessRoleCreate,
    access_roles_service: AccessRolesService = Depends(get_access_roles_service)
) -> AccessRole:
    try:
        return access_roles_service.create_access_role(access_role)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Access role with this name already exists')


@router.get(
    "/{access_role_id}",
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN])],
    response_model=AccessRole
)
def get_access_role(
    access_role_id: UUID,
    access_roles_service: AccessRolesService = Depends(get_access_roles_service)
) -> AccessRole:
    access_role = access_roles_service.get_access_role(access_role_id)
    if not access_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Access role not found')
    return access_role


@router.delete(
    "/{access_role_id}",
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_access_role(
    access_role_id: UUID,
    access_roles_service: AccessRolesService = Depends(get_access_roles_service)
) -> None:
    access_role = access_roles_service.get_access_role(access_role_id)
    if not access_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Access role not found')
    access_roles_service.delete_access_role(access_role_id)


@router.get(
    "/{access_role_id}/access-scopes",
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN])],
    response_model=List[AccessScope]
)
def list_access_role_access_scopes(
    access_role_id: UUID,
    access_role_access_scopes_service: AccessRoleAccessScopesService = Depends(get_access_role_access_scopes_service)
) -> List[AccessScope]:
    return access_role_access_scopes_service.get_access_scopes_for_access_role(access_role_id)


@router.put(
    "/{access_role_id}/access-scopes",
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN])],
    response_model=List[AccessScope]
)
def update_access_role_access_scopes(
    access_role_id: UUID,
    access_scopes: List[AccessScope],
    access_role_access_scopes_service: AccessRoleAccessScopesService = Depends(get_access_role_access_scopes_service),
    access_roles_service: AccessRolesService = Depends(get_access_roles_service)
) -> List[AccessScope]:
    access_role = access_roles_service.get_access_role(access_role_id)
    if not access_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Access role not found')
    access_role_access_scopes = access_role_access_scopes_service.update_access_role_access_scopes(access_role_id, access_scopes)
    return [access_role_access_scope.access_scope for access_role_access_scope in access_role_access_scopes]
