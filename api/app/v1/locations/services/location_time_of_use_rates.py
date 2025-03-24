from datetime import datetime, timedelta
from typing import List
from uuid import UUID

from app.v1.locations.repositories.location_time_of_use_rates_repository import LocationTimeOfUseRatesRepository
from app.v1.locations.schemas.location_time_of_use_rate import LocationTimeOfUseRate, LocationTimeOfUseRateCreate, LocationTimeOfUseRateUpdate


class LocationTimeOfUseRatesService:

    def __init__(self, location_time_of_use_rates_repository: LocationTimeOfUseRatesRepository):
        self.location_time_of_use_rates_repository = location_time_of_use_rates_repository

    def _do_int_ranges_intersect(
        self,
        start1: int | float,
        end1: int | float,
        start2: int | float,
        end2: int | float
    ) -> bool:
        return (
            start1 <= start2 < end1
            or start1 < end2 <= end1
            or start2 <= start1 < end2
        )

    def _do_datetime_ranges_intersect(
        self,
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        return self._do_int_ranges_intersect(
            start1.timestamp(),
            end1.timestamp(),
            start2.timestamp(),
            end2.timestamp()
        )
        
    def _do_recurring_periods_intersect(
        self,
        new_rate: LocationTimeOfUseRateCreate,
        existing_rate: LocationTimeOfUseRate
    ) -> bool:
        new_rate_end_at = new_rate.end_at + timedelta(days=1)
        existing_rate_end_at = existing_rate.end_at + timedelta(days=1)
        if new_rate.recurs_yearly and existing_rate.recurs_yearly:
            return self._do_datetime_ranges_intersect(
                new_rate.start_at,
                new_rate_end_at,
                existing_rate.start_at.replace(year=new_rate.start_at.year),
                existing_rate_end_at.replace(year=new_rate_end_at.year)
            )
        
        if new_rate.recurs_yearly and not existing_rate.recurs_yearly:
            for year_to_check in range(existing_rate.start_at.year, existing_rate_end_at.year + 1):
                if self._do_datetime_ranges_intersect(
                    new_rate.start_at.replace(year=year_to_check),
                    new_rate_end_at.replace(year=year_to_check),
                    existing_rate.start_at,
                    existing_rate_end_at
                ):
                    return True
            return False
        
        if not new_rate.recurs_yearly and existing_rate.recurs_yearly:
            for year_to_check in range(new_rate.start_at.year, new_rate_end_at.year + 1):
                if self._do_datetime_ranges_intersect(
                    new_rate.start_at,
                    new_rate_end_at,
                    existing_rate.start_at.replace(year=year_to_check),
                    existing_rate_end_at.replace(year=year_to_check)
                ):
                    return True
            return False
        
        return self._do_datetime_ranges_intersect(
            new_rate.start_at,
            new_rate_end_at,
            existing_rate.start_at,
            existing_rate_end_at
        )
    
    def _do_location_time_of_use_rates_intersect(
        self,
        new_rate: LocationTimeOfUseRateCreate,
        existing_rate: LocationTimeOfUseRate
    ) -> bool:
        if not self._do_recurring_periods_intersect(new_rate, existing_rate):
            return False
        
        if len(set(new_rate.days_of_week).intersection(existing_rate.days_of_week)) == 0:
            return False
        
        return self._do_int_ranges_intersect(
            new_rate.day_started_at_seconds,
            new_rate.day_ended_at_seconds,
            existing_rate.day_started_at_seconds,
            existing_rate.day_ended_at_seconds
        )

    def create_location_time_of_use_rate(self, location_time_of_use_rate_create: LocationTimeOfUseRateCreate) -> LocationTimeOfUseRate:
        active_rates = self.location_time_of_use_rates_repository.get_active_location_time_of_use_rates(location_time_of_use_rate_create.location_id)
        if active_rates:
            conflicting_rates = [
                active_rate
                for active_rate in active_rates
                if self._do_location_time_of_use_rates_intersect(location_time_of_use_rate_create, active_rate)
            ]
            if conflicting_rates:
                raise ValueError("New rate conflicts with existing active rates")

        return self.location_time_of_use_rates_repository.create_location_time_of_use_rate(location_time_of_use_rate_create)
    
    def get_location_time_of_use_rate(self, location_time_of_use_rate_id: UUID) -> LocationTimeOfUseRate:
        return self.location_time_of_use_rates_repository.get_location_time_of_use_rate(location_time_of_use_rate_id)

    def get_location_time_of_use_rates(self, location_id: UUID) -> List[LocationTimeOfUseRate]:
        return self.location_time_of_use_rates_repository.get_location_time_of_use_rates(location_id)
    
    def get_active_location_time_of_use_rates(self, location_id: UUID) -> List[LocationTimeOfUseRate]:
        return self.location_time_of_use_rates_repository.get_active_location_time_of_use_rates(location_id)
    
    def update_location_time_of_use_rate(self, location_time_of_use_rate_update: LocationTimeOfUseRateUpdate) -> LocationTimeOfUseRate:
        location_time_of_use_rate = self.location_time_of_use_rates_repository.get_location_time_of_use_rate(location_time_of_use_rate_update.location_time_of_use_rate_id)
        if location_time_of_use_rate_update.is_active == location_time_of_use_rate.is_active:
            return location_time_of_use_rate

        if location_time_of_use_rate_update.is_active:
            temp_location_time_of_use_create = LocationTimeOfUseRateCreate(
                location_id=location_time_of_use_rate.location_id,
                days_of_week=location_time_of_use_rate.days_of_week,
                is_active=location_time_of_use_rate_update.is_active,
                comment=location_time_of_use_rate.comment,
                price_per_kwh=location_time_of_use_rate.price_per_kwh,
                day_started_at_seconds=location_time_of_use_rate.day_started_at_seconds,
                day_ended_at_seconds=location_time_of_use_rate.day_ended_at_seconds,
                start_at=location_time_of_use_rate.start_at,
                end_at=location_time_of_use_rate.end_at,
                recurs_yearly=location_time_of_use_rate.recurs_yearly
            )
            active_rates = self.location_time_of_use_rates_repository.get_active_location_time_of_use_rates(location_time_of_use_rate.location_id)
            if active_rates:
                conflicting_rates = [
                    active_rate
                    for active_rate in active_rates
                    if self._do_location_time_of_use_rates_intersect(temp_location_time_of_use_create, active_rate)
                ]
                if conflicting_rates:
                    raise ValueError("Updated rate conflicts with existing active rates")

        return self.location_time_of_use_rates_repository.update_location_time_of_use_rate(location_time_of_use_rate_update)