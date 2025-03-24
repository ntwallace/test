from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Security, status

from app.v1.appliances.services.appliance_type import ApplianceTypesService
from app.v1.dependencies import get_appliance_types_service, verify_any_authorization, verify_jwt_authorization
from app.v1.appliances.schemas.appliance_type import ApplianceType, ApplianceTypeCreate
from app.v1.schemas import AccessScope


router = APIRouter(tags=['appliances'])


@router.post(
    '/',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.ADMIN, AccessScope.APPLIANCES_WRITE])],
    response_model=ApplianceType,
    status_code=status.HTTP_201_CREATED
)
def create_appliance_type(appliance_type: ApplianceTypeCreate,
                          appliance_type_service: ApplianceTypesService = Depends(get_appliance_types_service)):
    appliance_type_check = appliance_type_service.get_appliance_by_make_model_type_subtype_year(appliance_type.make, appliance_type.model, appliance_type.type, appliance_type.subtype, appliance_type.year_manufactured)
    if appliance_type_check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Appliance type already exists')
    return appliance_type_service.create_appliance_type(appliance_type)


@router.get(
    '/{appliance_type_id}',
    dependencies=[Security(verify_any_authorization, scopes=[AccessScope.APPLIANCES_READ])],
    response_model=ApplianceType,
)
def get_appliance_type(appliance_type_id: UUID,
                       appliances_service: ApplianceTypesService = Depends(get_appliance_types_service)):
    appliance_type = appliances_service.get_appliance_type_by_id(appliance_type_id)
    if appliance_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Appliance not found')
    return appliance_type


@router.delete(
    '/{appliance_type_id}',
    dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.APPLIANCES_WRITE])],
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_appliance_type(appliance_type_id: UUID,
                          appliance_type_service: ApplianceTypesService = Depends(get_appliance_types_service)):
    appliance_type = appliance_type_service.get_appliance_type_by_id(appliance_type_id)
    if appliance_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Appliance type not found')
    appliance_type_service.delete_appliance_type(appliance_type_id)
    return None
