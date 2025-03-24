from fastapi import APIRouter, Depends, HTTPException, Security, status
from uuid import UUID
from sqlalchemy.exc import IntegrityError

from app.v1.dependencies import get_hvac_equipment_types_service, verify_jwt_authorization
from app.v1.hvac.schemas.hvac_equipment_type import HvacEquipmentTypeCreate
from app.v1.hvac.services.hvac_equipment_types import HvacEquipmentTypesService
from app.v1.schemas import AccessScope


router = APIRouter(tags=['hvac'])


@router.post('/',
             dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_WRITE])],
             status_code=status.HTTP_201_CREATED)
def create_hvac_equipment_type(hvac_equipment_type: HvacEquipmentTypeCreate,
                               hvac_equipment_types_service: HvacEquipmentTypesService = Depends(get_hvac_equipment_types_service)):
    try:
        hvac_equipment_type_schema = hvac_equipment_types_service.create_hvac_equipment_type(hvac_equipment_type)
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Hvac equipment type already exists')

    return hvac_equipment_type_schema


@router.get('/{equipment_type_id}',
            dependencies=[Security(verify_jwt_authorization, scopes=[AccessScope.HVAC_READ])])
def get_hvac_equipment_type_by_id(equipment_type_id: UUID,
                                  hvac_equipment_types_service: HvacEquipmentTypesService = Depends(get_hvac_equipment_types_service)):
    hvac_equipment_type = hvac_equipment_types_service.get_hvac_equipment_type_by_id(equipment_type_id)
    if not hvac_equipment_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Hvac equipment type not found')
    return hvac_equipment_type


@router.delete('/{equipment_type_id}',
               dependencies=[
                   Security(verify_jwt_authorization, scopes=[AccessScope.ADMIN, AccessScope.HVAC_WRITE])],
               status_code=status.HTTP_204_NO_CONTENT)
def delete_hvac_equipment_type(equipment_type_id: UUID,
                               hvac_equipment_types_service: HvacEquipmentTypesService = Depends(get_hvac_equipment_types_service)):
    hvac_equipment_type = hvac_equipment_types_service.get_hvac_equipment_type_by_id(equipment_type_id)
    if hvac_equipment_type is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Hvac equipment type not found')
    hvac_equipment_types_service.delete_hvac_equipment_type(equipment_type_id)
    return None
