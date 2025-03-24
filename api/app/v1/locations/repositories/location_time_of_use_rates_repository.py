from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.v1.locations.models.location_time_of_use_rate import LocationTimeOfUseRate as LocationTimeOfUseRateModel
from app.v1.locations.schemas.location_time_of_use_rate import LocationTimeOfUseRate, LocationTimeOfUseRateCreate, LocationTimeOfUseRateUpdate


class LocationTimeOfUseRatesRepository(ABC):

    @abstractmethod
    def create_location_time_of_use_rate(self, location_time_of_use_rate: LocationTimeOfUseRateCreate) -> LocationTimeOfUseRate:
        pass

    @abstractmethod
    def get_location_time_of_use_rate(self, location_time_of_use_rate_id: UUID) -> LocationTimeOfUseRate:
        pass

    @abstractmethod
    def get_active_location_time_of_use_rates(self, location_id: UUID) -> List[LocationTimeOfUseRate]:
        pass

    @abstractmethod
    def get_location_time_of_use_rates(self, location_id: UUID) -> List[LocationTimeOfUseRate]:
        pass

    @abstractmethod
    def update_location_time_of_use_rate(self, location_time_of_use_rate_update: LocationTimeOfUseRateUpdate) -> LocationTimeOfUseRate:
        pass


class PostgresLocationTimeOfUseRatesRepository(LocationTimeOfUseRatesRepository):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_location_time_of_use_rate(self, location_time_of_use_rate_create: LocationTimeOfUseRateCreate) -> LocationTimeOfUseRate:
        location_time_of_use_rate = LocationTimeOfUseRateModel(
            location_id=location_time_of_use_rate_create.location_id,
            days_of_week=location_time_of_use_rate_create.days_of_week,
            is_active=location_time_of_use_rate_create.is_active,
            comment=location_time_of_use_rate_create.comment,
            price_per_kwh=location_time_of_use_rate_create.price_per_kwh,
            day_started_at_seconds=location_time_of_use_rate_create.day_started_at_seconds,
            day_ended_at_seconds=location_time_of_use_rate_create.day_ended_at_seconds,
            start_at=location_time_of_use_rate_create.start_at,
            end_at=location_time_of_use_rate_create.end_at,
            recurs_yearly=location_time_of_use_rate_create.recurs_yearly
        )
        self.db_session.add(location_time_of_use_rate)
        self.db_session.commit()
        self.db_session.refresh(location_time_of_use_rate)
        return LocationTimeOfUseRate.model_validate(location_time_of_use_rate, from_attributes=True)

    def get_location_time_of_use_rate(self, location_time_of_use_rate_id: UUID) -> LocationTimeOfUseRate:
        location_time_of_use_rate = self.db_session.query(LocationTimeOfUseRateModel).filter(
            LocationTimeOfUseRateModel.location_time_of_use_rate_id==location_time_of_use_rate_id
        ).first()
        return LocationTimeOfUseRate.model_validate(location_time_of_use_rate, from_attributes=True)

    def get_active_location_time_of_use_rates(self, location_id: UUID) -> List[LocationTimeOfUseRate]:
        location_time_of_use_rates = self.db_session.query(LocationTimeOfUseRateModel).filter(
            LocationTimeOfUseRateModel.location_id==location_id,
            LocationTimeOfUseRateModel.is_active.is_(True)
        ).all()
        return [
            LocationTimeOfUseRate.model_validate(location_time_of_use_rate, from_attributes=True)
            for location_time_of_use_rate in location_time_of_use_rates
        ]
            
    def get_location_time_of_use_rates(self, location_id: UUID) -> List[LocationTimeOfUseRate]:
        location_time_of_use_rates = self.db_session.query(LocationTimeOfUseRateModel).filter(
            LocationTimeOfUseRateModel.location_id==location_id
        ).order_by(LocationTimeOfUseRateModel.start_at).all()
        return [
            LocationTimeOfUseRate.model_validate(location_time_of_use_rate, from_attributes=True)
            for location_time_of_use_rate in location_time_of_use_rates
        ]

    def update_location_time_of_use_rate(self, location_time_of_use_rate_update: LocationTimeOfUseRateUpdate) -> LocationTimeOfUseRate:
        location_time_of_use_rate = self.db_session.query(LocationTimeOfUseRateModel).filter(
            LocationTimeOfUseRateModel.location_time_of_use_rate_id==location_time_of_use_rate_update.location_time_of_use_rate_id
        ).first()
        if location_time_of_use_rate is None:
            raise NotFoundError("Location time of use rate not found")
        location_time_of_use_rate.is_active = location_time_of_use_rate_update.is_active
        self.db_session.commit()
        self.db_session.refresh(location_time_of_use_rate)
        return LocationTimeOfUseRate.model_validate(location_time_of_use_rate, from_attributes=True)
