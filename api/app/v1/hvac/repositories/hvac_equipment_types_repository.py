from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.hvac.models.hvac_equipment_type import HvacEquipmentTypes as HvacEquipmentTypesModel
from app.v1.hvac.schemas.hvac_equipment_type import HvacEquipmentType, HvacEquipmentTypeCreate


class HvacEquipmentTypesRepository(ABC):

    @abstractmethod
    def create(self, hvac_equipment_type_create: HvacEquipmentTypeCreate) -> HvacEquipmentType:
        ...
    
    @abstractmethod
    def get(self, hvac_equipment_type_id: UUID) -> Optional[HvacEquipmentType]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[HvacEquipmentType]:
        ...
    
    @abstractmethod
    def delete(self, hvac_equipment_type_id: UUID) -> None:
        ...


class PostgresHvacEquipmentTypesRepository(HvacEquipmentTypesRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, hvac_equipment_type_create: HvacEquipmentTypeCreate) -> HvacEquipmentType:
        hvac_equipment_type = HvacEquipmentTypesModel(
            make=hvac_equipment_type_create.make,
            model=hvac_equipment_type_create.model,
            type=hvac_equipment_type_create.type,
            subtype=hvac_equipment_type_create.subtype,
            year_manufactured=hvac_equipment_type_create.year_manufactured
        )
        self.session.add(hvac_equipment_type)
        self.session.commit()
        self.session.refresh(hvac_equipment_type)
        return HvacEquipmentType.model_validate(hvac_equipment_type, from_attributes=True)
    
    @final
    def get(self, hvac_equipment_type_id: UUID) -> Optional[HvacEquipmentType]:
        hvac_equipment_type = self.session.query(HvacEquipmentTypesModel).filter(HvacEquipmentTypesModel.hvac_equipment_type_id == hvac_equipment_type_id).first()
        if hvac_equipment_type is None:
            return None
        return HvacEquipmentType.model_validate(hvac_equipment_type, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[HvacEquipmentType]:
        hvac_equipment_types = self.session.query(HvacEquipmentTypesModel).filter_by(**kwargs).all()
        return [
            HvacEquipmentType.model_validate(hvac_equipment_type, from_attributes=True)
            for hvac_equipment_type in hvac_equipment_types
        ]
    
    @final
    def delete(self, hvac_equipment_type_id: UUID) -> None:
        hvac_equipment_type = self.session.query(HvacEquipmentTypesModel).filter(HvacEquipmentTypesModel.hvac_equipment_type_id == hvac_equipment_type_id).first()
        if hvac_equipment_type:
            self.session.delete(hvac_equipment_type)
            self.session.commit()
