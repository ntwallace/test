from typing import List
from uuid import UUID

from app.v1.appliances.repositories.appliances_repository import AppliancesRepository
from app.v1.appliances.schemas.appliance import Appliance, ApplianceCreate


class AppliancesService:

    def __init__(self, appliances_repository: AppliancesRepository):
        self.appliances_repository = appliances_repository
    
    def create_appliance(self, appliance_create: ApplianceCreate) -> Appliance:
        return self.appliances_repository.create(appliance_create)

    def get_appliances_by_location(self, location_id: UUID) -> List[Appliance]:
        return self.appliances_repository.filter_by(location_id=location_id)

    def get_appliance_by_id(self, appliance_id: UUID) -> Appliance | None:
        return self.appliances_repository.get(appliance_id)
    
    def get_appliance_by_attributes(
        self,
        appliance_type_id: UUID,
        location_id: UUID,
        circuit_id: UUID,
        temperature_sensor_place_id: UUID | None,
        serial: str | None
    ) -> Appliance | None:
        appliances = self.appliances_repository.filter_by(
            appliance_type_id=appliance_type_id,
            location_id=location_id,
            circuit_id=circuit_id,
            temperature_sensor_place_id=temperature_sensor_place_id,
            serial=serial
        )
        if len(appliances) == 0:
            return None
        if len(appliances) > 1:
            raise ValueError("More than one appliance found")
        return appliances[0]
    
    def delete_appliance(self, appliance_id: UUID) -> None:
        return self.appliances_repository.delete(appliance_id)
