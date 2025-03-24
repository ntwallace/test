from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.appliances.models.appliance import Appliance as ApplianceModel
from app.v1.appliances.schemas.appliance import Appliance, ApplianceCreate


class AppliancesRepository(ABC):

    @abstractmethod
    def create(self, appliance_create: ApplianceCreate) -> Appliance:
        ...
    
    @abstractmethod
    def get(self, appliance_id: UUID) -> Optional[Appliance]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[Appliance]:
        ...
    
    @abstractmethod
    def delete(self, appliance_id: UUID) -> None:
        ...


class PostgresAppliancesRepository(AppliancesRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, appliance_create: ApplianceCreate) -> Appliance:
        appliance = ApplianceModel(
            name=appliance_create.name,
            appliance_super_type=appliance_create.appliance_super_type,
            appliance_type_id=appliance_create.appliance_type_id,
            location_id=appliance_create.location_id,
            circuit_id=appliance_create.circuit_id,
            temperature_sensor_place_id=appliance_create.temperature_sensor_place_id,
            serial=appliance_create.serial
        )
        self.session.add(appliance)
        self.session.commit()
        self.session.refresh(appliance)
        return Appliance.model_validate(appliance)
    
    @final
    def get(self, appliance_id: UUID) -> Optional[Appliance]:
        appliance = self.session.query(ApplianceModel).filter(ApplianceModel.appliance_id == appliance_id).first()
        if appliance is None:
            return None
        return Appliance.model_validate(appliance)
    
    @final
    def filter_by(self, **kwargs) -> List[Appliance]:
        appliances = self.session.query(ApplianceModel).filter_by(**kwargs).all()
        return [
            Appliance.model_validate(appliance, from_attributes=True)
            for appliance in appliances
        ]

    @final
    def delete(self, appliance_id: UUID) -> None:
        appliance = self.session.query(ApplianceModel).filter(ApplianceModel.appliance_id == appliance_id).first()
        self.session.delete(appliance)
        self.session.commit()
        return None
