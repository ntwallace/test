import logging
from typing import Annotated, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Security, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.auth.schemas.organization_access_grant import OrganizationAccessGrant
from app.v1.auth.services.user_organization_access_grants import UserOrganizationAccessGrantsService
from app.v1.dependencies import (
    get_access_token_data_or_raise,
    get_organization_users_service,
    get_organization_feature_toggles_service,
    get_organizations_service,
    get_access_token_data,
    get_user_access_grants_helper,
    get_user_organization_access_grants_service,
    get_users_service,
    verify_any_authorization,
    verify_jwt_authorization
)
from app.v1.organizations.schemas.organization import Organization, OrganizationCreate
from app.v1.organizations.schemas.organization_feature_toggle import OrganizationFeatureToggle, OrganizationFeatureToggleEnum
from app.v1.organizations.schemas.organization_user import OrganizationUser, OrganizationUserCreate
from app.v1.organizations.services.organization_feature_toggles import OrganizationFeatureTogglesService
from app.v1.organizations.services.organization_users import OrganizationUsersService
from app.v1.organizations.services.organizations import OrganizationsService
from app.v1.schemas import AccessScope, AccessTokenData
from app.v1.users.services.users import UsersService


logger = logging.getLogger()
logger.setLevel(logging.INFO)


router = APIRouter(tags=['organizations'])


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.ORGANIZATIONS_WRITE])],
    response_model=Organization,
    status_code=status.HTTP_201_CREATED
)
def create_organization(
    organization: OrganizationCreate,
    organizations_service: OrganizationsService = Depends(get_organizations_service),
    users_service: UsersService = Depends(get_users_service),
    organization_users_service: OrganizationUsersService = Depends(get_organization_users_service),
    user_organization_access_grants_service: UserOrganizationAccessGrantsService = Depends(get_user_organization_access_grants_service),
):
    try:
        organization_schema = organizations_service.create_organization(organization)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Organization already exists')
    
    support_user = users_service.get_user_by_email('support@powerx.co')
    if support_user is None:
        logger.warning('Could not find support user')
    else:
        # Set support user to organization owner
        organization_users_service.create_organization_user(
            OrganizationUserCreate(
                organization_id=organization_schema.organization_id,
                user_id=support_user.user_id,
                is_organization_owner=True
            )
        )
        # Add all access grants to support user
        user_organization_access_grants_service.add_user_organization_access_grants(
            user_id=support_user.user_id,
            organization_id=organization_schema.organization_id,
            access_grants=[
                OrganizationAccessGrant.ALLOW_CREATE_LOCATION,
                OrganizationAccessGrant.ALLOW_READ_LOCATION,
                OrganizationAccessGrant.ALLOW_UPDATE_LOCATION,
                OrganizationAccessGrant.ALLOW_READ_ORGANIZATION,
                OrganizationAccessGrant.ALLOW_UPDATE_ORGANIZATION
            ]
        )
    
    return organization_schema


@router.get(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.ORGANIZATIONS_READ])],
    response_model=List[Organization]
)
def get_organizations(
    name: Annotated[str | None, Query()] = None,
    organizations_service: OrganizationsService = Depends(get_organizations_service)
):
    organizations = organizations_service.get_organizations(name=name)
    return organizations


@router.get(
    '/{organization_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ORGANIZATIONS_READ])],
    response_model=Organization
)
def get_organization(organization_id: UUID,
                     organizations_service: OrganizationsService = Depends(get_organizations_service),
                     token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
                     user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)):
    organization = organizations_service.get_organization_by_organization_id(organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Organization not found')
    
    if token_data is None:
        return organization

    if AccessScope.ADMIN in token_data.access_scopes:
        return organization
    
    if not user_access_grants_helper.is_user_authorized_for_organization_read(token_data.user_id, organization.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    
    return organization


@router.post(
    '/{organization_id}/users',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ORGANIZATION_USERS_WRITE])],
    response_model=OrganizationUser,
    status_code=status.HTTP_201_CREATED
)
def create_organization_user(organization_id: UUID,
                             organization_user: OrganizationUserCreate,
                             organizations_service: OrganizationsService = Depends(get_organizations_service),
                             organization_users_service: OrganizationUsersService = Depends(get_organization_users_service),
                             token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
                             user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)):
    if (AccessScope.ADMIN not in token_data.access_scopes
        and not user_access_grants_helper.is_user_authorized_for_organization_update(token_data.user_id, organization_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')

    organization = organizations_service.get_organization_by_organization_id(organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Organization not found')

    organization_user_check = organization_users_service.get_organization_user(organization_id, organization_user.user_id)
    if organization_user_check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Organization user already exists')

    organization_user_schema = organization_users_service.create_organization_user(organization_user)
    return organization_user_schema


@router.get(
    '/{organization_id}/users',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ORGANIZATION_USERS_READ])],
    response_model=List[OrganizationUser]
)
def get_organization_users(
    organization_id: UUID,
    access_token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
    organizations_service: OrganizationsService = Depends(get_organizations_service),
    organization_users_service: OrganizationUsersService = Depends(get_organization_users_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if (access_token_data is not None
        and AccessScope.ADMIN not in access_token_data.access_scopes
        and not user_access_grants_helper.is_user_authorized_for_organization_read(access_token_data.user_id, organization_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    
    organization = organizations_service.get_organization_by_organization_id(organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Organization not found')
    
    users = organization_users_service.get_organization_users(organization_id)
    return users


@router.get(
    '/{organization_id}/users/{user_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ORGANIZATION_USERS_READ])],
    response_model=OrganizationUser
)
def get_organization_user(organization_id: UUID,
                          user_id: UUID,
                          organizations_service: OrganizationsService = Depends(get_organizations_service),
                          organization_users_service: OrganizationUsersService = Depends(get_organization_users_service),
                          token_data: AccessTokenData = Depends(get_access_token_data_or_raise),
                          user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)):
    if (AccessScope.ADMIN not in token_data.access_scopes
        and not user_access_grants_helper.is_user_authorized_for_organization_read(token_data.user_id, organization_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    
    organization = organizations_service.get_organization_by_organization_id(organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Organization not found')

    user = organization_users_service.get_organization_user(organization_id, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Organization user not found')
    
    return user


@router.delete(
    '/{organization_id}/users/{user_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ORGANIZATION_USERS_WRITE])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_organization_user(organization_id: UUID,
                             user_id: UUID,
                             organizations_service: OrganizationsService = Depends(get_organizations_service),
                             organization_users_service: OrganizationUsersService = Depends(get_organization_users_service),
                             token_data: AccessTokenData = Depends(get_access_token_data),
                             user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)):
    if (AccessScope.ADMIN not in token_data.access_scopes
        and not user_access_grants_helper.is_user_authorized_for_organization_update(token_data.user_id, organization_id)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    
    organization = organizations_service.get_organization_by_organization_id(organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Organization not found')
    
    user = organization_users_service.get_organization_user(organization_id, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Organization user not found')
    
    organization_users_service.delete_organization_user(organization_id, user_id)
    return None


@router.put(
    '/{organization_id}/feature-toggles',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.ORGANIZATIONS_WRITE])],
    response_model=OrganizationFeatureToggle
)
def put_organization_feature_toggle(
    organization_id: UUID,
    feature_toggle: OrganizationFeatureToggleEnum,
    is_enabled: bool = True,
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    organization_feature_toggles_service: OrganizationFeatureTogglesService = Depends(get_organization_feature_toggles_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper),
):
    if not user_access_grants_helper.is_user_authorized_for_organization_update(access_token_data.user_id, organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')

    organization_feature_toggle = organization_feature_toggles_service.set_feature_toggle_for_organization(organization_id, feature_toggle, is_enabled)
    return organization_feature_toggle

@router.get(
    '/{organization_id}/feature-toggles',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ORGANIZATIONS_READ])],
    response_model=List[OrganizationFeatureToggle]
)
def get_organization_feature_toggles(
    organization_id: UUID,
    organization_feature_toggles_service: OrganizationFeatureTogglesService = Depends(get_organization_feature_toggles_service),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper),
):
    if not user_access_grants_helper.is_user_authorized_for_organization_read(access_token_data.user_id, organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Forbidden')
    
    organization_feature_toggles = organization_feature_toggles_service.get_feature_toggles_for_organization(organization_id)
    return organization_feature_toggles