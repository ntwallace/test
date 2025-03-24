from typing import List
from uuid import UUID

from app.v1.locations.repositories.location_operating_hours_repository import LocationOperatingHoursRepository
from app.v1.locations.schemas.location_operating_hours import LocationOperatingHoursCreate, LocationOperatingHours, LocationOperatingHoursUpdate

class LocationOperatingHoursService:

    def __init__(self, location_operating_hours_repository: LocationOperatingHoursRepository):
        self.location_operating_hours_repository = location_operating_hours_repository
    
    def create_location_operating_hours(self, location_operating_hours_create: LocationOperatingHoursCreate) -> LocationOperatingHours:
        return self.location_operating_hours_repository.create(location_operating_hours_create)
    
    def get_location_operating_hours_for_location(self, location_id: UUID) -> List[LocationOperatingHours]:
        return self.location_operating_hours_repository.filter_by(location_id=location_id)
    
    def update_location_operating_hours(self, location_operating_hours_update: LocationOperatingHoursUpdate) -> LocationOperatingHours:
        updated_location_operating_hours = self.location_operating_hours_repository.update(
            location_id=location_operating_hours_update.location_id,
            day_of_week=location_operating_hours_update.day_of_week,
            is_open=location_operating_hours_update.is_open,
            work_start_time=location_operating_hours_update.work_start_time,
            open_time=location_operating_hours_update.open_time,
            close_time=location_operating_hours_update.close_time,
            work_end_time=location_operating_hours_update.work_end_time
        )
        if updated_location_operating_hours is None:
            raise ValueError(f"Location operating hours with location_id {location_operating_hours_update.location_id} and day_of_week {location_operating_hours_update.day_of_week} not found")
        return updated_location_operating_hours
    
    def delete_location_operating_hours_for_location(self, location_id: UUID) -> None:
        self.location_operating_hours_repository.delete_all_for_location(location_id=location_id)
