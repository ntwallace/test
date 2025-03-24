from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.v1.locations.models.location_electricity_price import LocationElectricityPrice as LocationElectricityPriceModel
from app.v1.locations.schemas.location_electricity_price import LocationElectricityPrice, LocationElectricityPriceCreate, LocationElectricityPriceUpdate


class LocationElectricityPricesRepository(ABC):

    @abstractmethod
    def create_location_electricity_price(self, location_electricity_price_create: LocationElectricityPriceCreate) -> LocationElectricityPrice:
        pass

    @abstractmethod
    def update_location_electricity_price(self, location_electricity_price_update: LocationElectricityPriceUpdate) -> LocationElectricityPrice:
        pass

    @abstractmethod
    def get_current_location_electricity_price(self, location_id: UUID) -> Optional[LocationElectricityPrice]:
        pass

    @abstractmethod
    def get_location_electricity_prices(self, location_id: UUID, min_end_at: datetime) -> List[LocationElectricityPrice]:
        pass

    @abstractmethod
    def filter_by(self, **kwargs) -> List[LocationElectricityPrice]:
        pass


class PostgresLocationElectricityPricesRepository(LocationElectricityPricesRepository):

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_location_electricity_price(self, location_electricity_price_create: LocationElectricityPriceCreate) -> LocationElectricityPrice:
        location_electricity_price = LocationElectricityPriceModel(
            location_id=location_electricity_price_create.location_id,
            comment=location_electricity_price_create.comment,
            price_per_kwh=location_electricity_price_create.price_per_kwh,
            started_at=location_electricity_price_create.started_at,
            ended_at=location_electricity_price_create.ended_at
        )
        self.db_session.add(location_electricity_price)
        self.db_session.commit()
        self.db_session.refresh(location_electricity_price)
        return LocationElectricityPrice.model_validate(location_electricity_price, from_attributes=True)

    def update_location_electricity_price(self, location_electricity_price_update: LocationElectricityPriceUpdate) -> LocationElectricityPrice:
        location_electricity_price = self.db_session.query(LocationElectricityPriceModel).filter(
            LocationElectricityPriceModel.location_electricity_price_id == location_electricity_price_update.location_electricity_price_id
        ).first()
        if location_electricity_price is None:
            raise NotFoundError('Location electricity price not found')
        location_electricity_price.ended_at = location_electricity_price_update.ended_at
        self.db_session.commit()
        self.db_session.refresh(location_electricity_price)
        return LocationElectricityPrice.model_validate(location_electricity_price, from_attributes=True)
    
    def get_current_location_electricity_price(self, location_id: UUID) -> Optional[LocationElectricityPrice]:
        location_electricity_prices = self.db_session.query(LocationElectricityPriceModel).filter(
            LocationElectricityPriceModel.location_id == location_id,
            or_(
                LocationElectricityPriceModel.ended_at.is_(None),
                LocationElectricityPriceModel.ended_at > datetime.now()
            )
        ).all()

        if len(location_electricity_prices) == 0:
            return None
        elif len(location_electricity_prices) > 1:
            raise Exception('Multiple current location electricity prices found')
        
        return LocationElectricityPrice.model_validate(location_electricity_prices[0], from_attributes=True)

    def get_location_electricity_prices(self, location_id: UUID, min_end_at_exclusive: datetime) -> List[LocationElectricityPrice]:
        location_electricity_prices = self.db_session.query(
            LocationElectricityPriceModel
        ).filter(
            LocationElectricityPriceModel.location_id == location_id,
            or_(
                LocationElectricityPriceModel.ended_at.is_(None),
                LocationElectricityPriceModel.ended_at > min_end_at_exclusive
            )
        ).all()
        return [LocationElectricityPrice.model_validate(location_electricity_price, from_attributes=True) for location_electricity_price in location_electricity_prices]
    
    def filter_by(self, **kwargs) -> List[LocationElectricityPrice]:
        location_electricity_prices = self.db_session.query(LocationElectricityPriceModel).filter_by(**kwargs).all()
        return [LocationElectricityPrice.model_validate(location_electricity_price, from_attributes=True) for location_electricity_price in location_electricity_prices]
