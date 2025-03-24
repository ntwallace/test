from typing import List
from uuid import UUID

from app.v1.hvac.repositories.hvac_zones_repository import HvacZonesRepository
from app.v1.hvac.schemas.hvac_zone import HvacZone, HvacZoneCreate


class HvacZonesService:

    def __init__(self, hvac_zones_repository: HvacZonesRepository):
        self.hvac_zones_repository = hvac_zones_repository
    
    def create_hvac_zone(self, hvac_zone_create: HvacZoneCreate) -> HvacZone:
        return self.hvac_zones_repository.create(hvac_zone_create)

    def get_hvac_zone_by_id(self, hvac_zone_id: UUID) -> HvacZone | None:
        return self.hvac_zones_repository.get(hvac_zone_id)

    def get_hvac_zone_by_attributes(self, name: str, location_id: UUID) -> HvacZone | None:
        hvac_zones = self.hvac_zones_repository.filter_by(name=name, location_id=location_id)
        if len(hvac_zones) == 0:
            return None
        if len(hvac_zones) > 1:
            raise ValueError('Multiple hvac zones found')
        return hvac_zones[0]

    def get_hvac_zones_by_location_id(self, location_id: UUID) -> List[HvacZone]:
        return self.hvac_zones_repository.filter_by(location_id=location_id)
    
    def filter_by(self, **kwargs) -> List[HvacZone]:
        return self.hvac_zones_repository.filter_by(**kwargs)

    def delete_hvac_zone(self, hvac_zone_id: UUID) -> None:
        self.hvac_zones_repository.delete(hvac_zone_id)
