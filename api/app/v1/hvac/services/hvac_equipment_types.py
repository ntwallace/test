from uuid import UUID

from app.v1.hvac.repositories.hvac_equipment_types_repository import HvacEquipmentTypesRepository
from app.v1.hvac.schemas.hvac_equipment_type import HvacEquipmentType, HvacEquipmentTypeCreate


class HvacEquipmentTypesService:

    def __init__(self, hvac_equipment_types_repository: HvacEquipmentTypesRepository):
        self.hvac_equipment_types_repository = hvac_equipment_types_repository

    def create_hvac_equipment_type(self, hvac_equipment_type_create: HvacEquipmentTypeCreate) -> HvacEquipmentType:
        return self.hvac_equipment_types_repository.create(hvac_equipment_type_create)

    def get_hvac_equipment_type_by_id(self, hvac_equipment_type_id: UUID) -> HvacEquipmentType | None:
        return self.hvac_equipment_types_repository.get(hvac_equipment_type_id)

    def get_hvac_equipment_type_by_make_model_type_subtype_year(
        self,
        make: str,
        model: str | None,
        type: str,
        subtype: str | None,
        year_manufactured: int | None
    ) -> HvacEquipmentType | None:
        hvac_equipment_types = self.hvac_equipment_types_repository.filter_by(
            make=make,
            model=model,
            type=type,
            subtype=subtype,
            year_manufactured=year_manufactured
        )
        if len(hvac_equipment_types) == 0:
            return None
        if len(hvac_equipment_types) > 1:
            raise ValueError('Multiple hvac equipment types found with matching attributes')
        return hvac_equipment_types[0]

    def delete_hvac_equipment_type(self, hvac_equipment_type_id: UUID) -> None:
        return self.hvac_equipment_types_repository.delete(hvac_equipment_type_id)
