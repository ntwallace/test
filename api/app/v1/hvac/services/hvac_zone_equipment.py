from uuid import UUID

from app.v1.hvac.repositories.hvac_zone_equipment_repository import HvacZoneEquipmentRepository
from app.v1.hvac.schemas.hvac_zone_equipment import HvacZoneEquipment, HvacZoneEquipmentCreate


class HvacZoneEquipmentService:

    def __init__(self, hvac_zone_equipment_repository: HvacZoneEquipmentRepository):
        self.hvac_zone_equipment_repository = hvac_zone_equipment_repository

    def create_hvac_zone_equipment(self, hvac_zone_equipment_create: HvacZoneEquipmentCreate) -> HvacZoneEquipment:
        return self.hvac_zone_equipment_repository.create(hvac_zone_equipment_create)

    def get_hvac_zone_equipment_by_id(self, hvac_zone_equipment_id: UUID) -> HvacZoneEquipment | None:
        return self.hvac_zone_equipment_repository.get(hvac_zone_equipment_id)

    def get_hvac_zone_equipment_by_attributes(
        self,
        hvac_zone_id: UUID,
        hvac_equipment_type_id: UUID
    ) -> HvacZoneEquipment | None:
        hvac_zone_equipment_list = self.hvac_zone_equipment_repository.filter_by(
            hvac_zone_id=hvac_zone_id,
            hvac_equipment_type_id=hvac_equipment_type_id
        )
        if len(hvac_zone_equipment_list) == 0:
            return None
        if len(hvac_zone_equipment_list) > 1:
            raise ValueError('Multiple hvac zone equipment found matching attributes')
        return hvac_zone_equipment_list[0]

    def get_hvac_zone_equipment_by_hvac_zone_id(self, hvac_zone_id: UUID) -> list[HvacZoneEquipment]:
        return self.hvac_zone_equipment_repository.filter_by(hvac_zone_id=hvac_zone_id)

    def delete_hvac_zone_equipment(self, hvac_zone_equipment_id: UUID) -> None:
        self.hvac_zone_equipment_repository.delete(hvac_zone_equipment_id)
