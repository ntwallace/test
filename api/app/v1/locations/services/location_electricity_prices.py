from datetime import datetime
from typing import List, Optional
from uuid import UUID

from app.v1.locations.repositories.location_electricity_prices_repository import LocationElectricityPricesRepository
from app.v1.locations.schemas.location_electricity_price import LocationElectricityPrice, LocationElectricityPriceCreate, LocationElectricityPriceUpdate


class LocationElectricityPricesService:

    def __init__(self, location_electricity_prices_repository: LocationElectricityPricesRepository):
        self.location_electricity_prices_repository = location_electricity_prices_repository
    
    def create_location_electricity_price(self, location_electricity_price_create: LocationElectricityPriceCreate) -> LocationElectricityPrice:
        current_location_electricity_price = self.location_electricity_prices_repository.get_current_location_electricity_price(location_electricity_price_create.location_id)
        if current_location_electricity_price:
            current_location_electricity_price_update = LocationElectricityPriceUpdate(
                location_electricity_price_id=current_location_electricity_price.location_electricity_price_id,
                ended_at=location_electricity_price_create.started_at
            )
            self.location_electricity_prices_repository.update_location_electricity_price(current_location_electricity_price_update)
        
        return self.location_electricity_prices_repository.create_location_electricity_price(location_electricity_price_create)

    def update_location_electricity_price(self, location_electricity_price_update: LocationElectricityPriceUpdate) -> LocationElectricityPrice:
        return self.location_electricity_prices_repository.update_location_electricity_price(location_electricity_price_update)

    def get_current_location_electricity_price(self, location_id: UUID) -> Optional[LocationElectricityPrice]:
        return self.location_electricity_prices_repository.get_current_location_electricity_price(location_id)
    
    def get_location_electricity_prices(self, location_id: UUID, min_end_at_exclusive: datetime) -> List[LocationElectricityPrice]:
        return self.location_electricity_prices_repository.get_location_electricity_prices(location_id, min_end_at_exclusive)
    
    def filter_by(self, **kwargs) -> List[LocationElectricityPrice]:
        return self.location_electricity_prices_repository.filter_by(**kwargs)
