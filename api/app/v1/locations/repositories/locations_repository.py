from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.locations.models.location import Location as LocationModel
from app.v1.locations.schemas.location import Location, LocationCreate


class LocationsRepository(ABC):

    @abstractmethod
    def create(self, location_create: LocationCreate) -> Location:
        ...
    
    @abstractmethod
    def get(self, location_id: UUID) -> Optional[Location]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[Location]:
        ...
    
    @abstractmethod
    def delete(self, location_id: UUID) -> None:
        ...


class PostgresLocationsRepository(LocationsRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, location_create: LocationCreate) -> Location:
        location = LocationModel(
            organization_id=location_create.organization_id,
            name=location_create.name,
            address=location_create.address,
            city=location_create.city,
            state=location_create.state,
            zip_code=location_create.zip_code,
            country=location_create.country,
            latitude=location_create.latitude,
            longitude=location_create.longitude,
            timezone=location_create.timezone,
        )
        self.session.add(location)
        self.session.commit()
        self.session.refresh(location)
        return Location.model_validate(location, from_attributes=True)

    @final
    def get(self, location_id: UUID) -> Optional[Location]:
        location = self.session.query(LocationModel).filter(LocationModel.location_id == location_id).first()
        if location:
            return Location.model_validate(location, from_attributes=True)
        return None
    
    @final
    def filter_by(self, **kwargs) -> List[Location]:
        locations = self.session.query(LocationModel).filter_by(**kwargs).all()
        return [
            Location.model_validate(location, from_attributes=True)
            for location in locations
        ]
    
    @final
    def delete(self, location_id: UUID) -> None:
        location = self.session.query(LocationModel).filter(LocationModel.location_id == location_id).first()
        if location:
            self.session.delete(location)
            self.session.commit()
