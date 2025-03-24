from typing import Optional
from uuid import UUID

from app.v1.appliances.repositories.appliance_types_repository import ApplianceTypesRepository
from app.v1.appliances.schemas.appliance_type import ApplianceType, ApplianceTypeCreate


class ApplianceTypesService:

    def __init__(self, appliance_types_repository: ApplianceTypesRepository):
        self.appliance_types_repository = appliance_types_repository
    
    def create_appliance_type(self, appliance_type_create: ApplianceTypeCreate) -> ApplianceType:
        return self.appliance_types_repository.create(appliance_type_create)
    
    def get_appliance_by_make_model_type_subtype_year(
        self,
        make: str,
        model: str | None,
        type: str,
        subtype: str | None,
        year_manufactured: int | None
    ) -> Optional[ApplianceType]:
        appliance_types = self.appliance_types_repository.filter_by(
            make=make,
            model=model,
            type=type,
            subtype=subtype,
            year_manufactured=year_manufactured
        )
        if len(appliance_types) == 0:
            return None
        if len(appliance_types) > 1:
            raise ValueError("More than one appliance type found")
        return appliance_types[0]
    
    def get_appliance_type_by_id(self, appliance_type_id: UUID) -> Optional[ApplianceType]:
        return self.appliance_types_repository.get(appliance_type_id)
    
    def delete_appliance_type(self, appliance_type_id: UUID) -> None:
        return self.appliance_types_repository.delete(appliance_type_id)
