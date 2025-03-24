from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.appliances.models.appliance_type import ApplianceType as ApplianceTypeModel
from app.v1.appliances.schemas.appliance_type import ApplianceType, ApplianceTypeCreate


class ApplianceTypesRepository(ABC):

    @abstractmethod
    def get(self, appliance_type_id: UUID) -> Optional[ApplianceType]:
        ...
    
    @abstractmethod
    def create(self, appliance_type_create: ApplianceTypeCreate) -> ApplianceType:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[ApplianceType]:
        ...
    
    @abstractmethod
    def delete(self, appliance_type_id: UUID) -> None:
        ...


class PostgresApplianceTypesRepository(ApplianceTypesRepository):
    
    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, appliance_type_create: ApplianceTypeCreate) -> ApplianceType:
        appliance_type = ApplianceTypeModel(
            make=appliance_type_create.make,
            model=appliance_type_create.model,
            type=appliance_type_create.type,
            subtype=appliance_type_create.subtype,
            year_manufactured=appliance_type_create.year_manufactured
        )
        self.session.add(appliance_type)
        self.session.commit()
        self.session.refresh(appliance_type)
        return ApplianceType.model_validate(appliance_type, from_attributes=True)

    @final
    def get(self, appliance_type_id: UUID) -> Optional[ApplianceType]:
        appliance_type = self.session.query(ApplianceTypeModel).filter(ApplianceTypeModel.appliance_type_id == appliance_type_id).first()
        if appliance_type is None:
            return None
        return ApplianceType.model_validate(appliance_type, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[ApplianceType]:
        appliance_types = self.session.query(ApplianceTypeModel).filter_by(**kwargs).all()
        return [
            ApplianceType.model_validate(appliance_type, from_attributes=True)
            for appliance_type in appliance_types
        ]

    @final
    def delete(self, appliance_type_id: UUID) -> None:
        appliance_type = self.session.query(ApplianceTypeModel).filter(ApplianceTypeModel.appliance_type_id == appliance_type_id).first()
        if appliance_type is not None:
            self.session.delete(appliance_type)
            self.session.commit()
