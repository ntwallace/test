from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.locations.models.location_operating_hours import LocationOperatingHours as LocationOperatingHoursModel
from app.v1.locations.schemas.location_operating_hours import LocationOperatingHours, LocationOperatingHoursCreate
from app.v1.schemas import DayOfWeek


class LocationOperatingHoursRepository(ABC):

    @abstractmethod
    def create(self, location_operating_hours_create: LocationOperatingHoursCreate) -> LocationOperatingHours:
        ...

    @abstractmethod
    def get(self, location_id: UUID, day_of_week: DayOfWeek) -> Optional[LocationOperatingHours]:
        ...

    @abstractmethod
    def filter_by(self, **kwargs) -> List[LocationOperatingHours]:
        ...
    
    @abstractmethod
    def update(self, location_id: UUID, day_of_week: DayOfWeek, **kwargs) -> Optional[LocationOperatingHours]:
        ...

    @abstractmethod
    def delete(self, location_id: UUID, day_of_week: DayOfWeek) -> None:
        ...
    
    @abstractmethod
    def delete_all_for_location(self, location_id: UUID) -> None:
        ...
    

class PostgresLocationOperatingHoursRepository(LocationOperatingHoursRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, location_operating_hours_create: LocationOperatingHoursCreate) -> LocationOperatingHours:
        location_operating_hours = LocationOperatingHoursModel(
            location_id=location_operating_hours_create.location_id,
            day_of_week=location_operating_hours_create.day_of_week,
            is_open=location_operating_hours_create.is_open,
            work_start_time=location_operating_hours_create.work_start_time,
            open_time=location_operating_hours_create.open_time,
            close_time=location_operating_hours_create.close_time,
            work_end_time=location_operating_hours_create.work_end_time
        )
        self.session.add(location_operating_hours)
        self.session.commit()
        self.session.refresh(location_operating_hours)
        return LocationOperatingHours.model_validate(location_operating_hours, from_attributes=True)
    
    @final
    def get(self, location_id: UUID, day_of_week: DayOfWeek) -> Optional[LocationOperatingHours]:
        location_operating_hours = self.session.query(LocationOperatingHoursModel).filter(LocationOperatingHoursModel.location_id == location_id, LocationOperatingHoursModel.day_of_week == day_of_week).first()
        if location_operating_hours is None:
            return None
        return LocationOperatingHours.model_validate(location_operating_hours, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[LocationOperatingHours]:
        location_operating_hours_list = self.session.query(LocationOperatingHoursModel).filter_by(**kwargs).all()
        return [
            LocationOperatingHours.model_validate(location_operating_hours, from_attributes=True)
            for location_operating_hours in location_operating_hours_list
        ]
    
    @final
    def update(self, location_id: UUID, day_of_week: DayOfWeek, **kwargs) -> Optional[LocationOperatingHours]:
        location_operating_hours = self.session.query(LocationOperatingHoursModel).filter(LocationOperatingHoursModel.location_id == location_id, LocationOperatingHoursModel.day_of_week == day_of_week).first()
        if location_operating_hours is None:
            return None
        for key, value in kwargs.items():
            setattr(location_operating_hours, key, value)
        self.session.commit()
        self.session.refresh(location_operating_hours)
        return LocationOperatingHours.model_validate(location_operating_hours, from_attributes=True)
    
    @final
    def delete(self, location_id: UUID, day_of_week: DayOfWeek) -> None:
        location_operating_hours = self.session.query(LocationOperatingHoursModel).filter(LocationOperatingHoursModel.location_id == location_id, LocationOperatingHoursModel.day_of_week == day_of_week).first()
        self.session.delete(location_operating_hours)
        self.session.commit()

    @final
    def delete_all_for_location(self, location_id: UUID) -> None:
        location_operating_hours_list = self.session.query(LocationOperatingHoursModel).filter(LocationOperatingHoursModel.location_id == location_id).all()
        for location_operating_hours in location_operating_hours_list:
            self.session.delete(location_operating_hours)
        self.session.commit()
