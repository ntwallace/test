from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.hvac.models.hvac_zone_equipment import HvacZoneEquipment as HvacZoneEquipmentModel
from app.v1.hvac.schemas.hvac_zone_equipment import HvacZoneEquipment, HvacZoneEquipmentCreate


class HvacZoneEquipmentRepository(ABC):

    @abstractmethod
    def create(self, hvac_zone_equipment_create: HvacZoneEquipmentCreate) -> HvacZoneEquipment:
        ...
    
    @abstractmethod
    def get(self, hvac_zone_equipment_id: UUID) -> Optional[HvacZoneEquipment]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[HvacZoneEquipment]:
        ...

    @abstractmethod
    def delete(self, hvac_zone_equipment_id: UUID) -> None:
        ...


class PostgresHvacZoneEquipmentRepository(HvacZoneEquipmentRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, hvac_zone_equipment_create: HvacZoneEquipmentCreate) -> HvacZoneEquipment:
        hvac_zone_equipment = HvacZoneEquipmentModel(
            hvac_zone_id=hvac_zone_equipment_create.hvac_zone_id,
            hvac_equipment_type_id=hvac_zone_equipment_create.hvac_equipment_type_id,
            circuit_id=hvac_zone_equipment_create.circuit_id,
            serial=hvac_zone_equipment_create.serial
        )
        self.session.add(hvac_zone_equipment)
        self.session.commit()
        self.session.refresh(hvac_zone_equipment)
        return HvacZoneEquipment.model_validate(hvac_zone_equipment, from_attributes=True)
    
    @final
    def get(self, hvac_zone_equipment_id: UUID) -> Optional[HvacZoneEquipment]:
        hvac_zone_equipment = self.session.query(HvacZoneEquipmentModel).filter(HvacZoneEquipmentModel.hvac_zone_equipment_id == hvac_zone_equipment_id).first()
        if hvac_zone_equipment is None:
            return None
        return HvacZoneEquipment.model_validate(hvac_zone_equipment, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[HvacZoneEquipment]:
        hvac_zone_equipment_rows = self.session.query(HvacZoneEquipmentModel).filter_by(**kwargs).all()
        return [
            HvacZoneEquipment.model_validate(hvac_zone_equipment, from_attributes=True)
            for hvac_zone_equipment in hvac_zone_equipment_rows
        ]
    
    @final
    def delete(self, hvac_zone_equipment_id: UUID) -> None:
        hvac_zone_equipment = self.session.query(HvacZoneEquipmentModel).filter(HvacZoneEquipmentModel.hvac_zone_equipment_id == hvac_zone_equipment_id).first()
        if hvac_zone_equipment:
            self.session.delete(hvac_zone_equipment)
            self.session.commit()
