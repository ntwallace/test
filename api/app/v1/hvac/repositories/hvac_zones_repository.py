from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.hvac.models.hvac_zone import HvacZone as HvacZoneModel
from app.v1.hvac.schemas.hvac_zone import HvacZone, HvacZoneCreate


class HvacZonesRepository(ABC):

    @abstractmethod
    def create(self, hvac_zone_create: HvacZoneCreate) -> HvacZone:
        ...

    @abstractmethod
    def get(self, hvac_zone_id: UUID) -> Optional[HvacZone]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[HvacZone]:
        ...
    
    @abstractmethod
    def delete(self, hvac_zone_id: UUID) -> None:
        ...


class PostgresHvacZonesRepository(HvacZonesRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, hvac_zone_create: HvacZoneCreate) -> HvacZone:
        hvac_zone = HvacZoneModel(
            name=hvac_zone_create.name,
            location_id=hvac_zone_create.location_id
        )
        try:
            self.session.add(hvac_zone)
            self.session.commit()
            self.session.refresh(hvac_zone)
            return HvacZone.model_validate(hvac_zone, from_attributes=True)
        except IntegrityError:
            raise ValueError('Hvac zone already exists')

    @final
    def get(self, hvac_zone_id: UUID) -> Optional[HvacZone]:
        hvac_zone = self.session.query(HvacZoneModel).filter(HvacZoneModel.hvac_zone_id == hvac_zone_id).first()
        if hvac_zone is None:
            return None
        return HvacZone.model_validate(hvac_zone, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[HvacZone]:
        hvac_zones = self.session.query(HvacZoneModel).filter_by(**kwargs).all()
        return [
            HvacZone.model_validate(hvac_zone, from_attributes=True)
            for hvac_zone in hvac_zones
        ]
    
    @final
    def delete(self, hvac_zone_id: UUID) -> None:
        hvac_zone = self.session.query(HvacZoneModel).filter(HvacZoneModel.hvac_zone_id == hvac_zone_id).first()
        if hvac_zone:
            self.session.delete(hvac_zone)
            self.session.commit()
