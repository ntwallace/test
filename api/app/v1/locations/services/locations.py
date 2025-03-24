from typing import List
from uuid import UUID

from app.v1.locations.repositories.locations_repository import LocationsRepository
from app.v1.locations.schemas.location import LocationCreate, Location as LocationSchema


class LocationsService:

    def __init__(self, locations_repository: LocationsRepository):
        self.locations_repository = locations_repository
    
    def create_location(self, location_create: LocationCreate) -> LocationSchema:
        return self.locations_repository.create(location_create)

    def get_location(self, location_id: UUID) -> LocationSchema | None:
        return self.locations_repository.get(location_id)
    
    def get_locations_by_organization_id(self, organization_id: UUID) -> List[LocationSchema]:
        return self.locations_repository.filter_by(organization_id=organization_id)
    
    def filter_by(self, **kwargs) -> List[LocationSchema]:
        return self.locations_repository.filter_by(**kwargs)
