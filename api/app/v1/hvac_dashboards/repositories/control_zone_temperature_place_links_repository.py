from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.hvac_dashboards.models.control_zone_temperature_place_link import ControlZoneTemperaturePlaceLink as ControlZoneTemperaturePlaceLinkModel
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import ControlZoneTemperaturePlaceLink, ControlZoneTemperaturePlaceLinkCreate


class ControlZoneTemperaturePlaceLinksRepository(ABC):

    @abstractmethod
    def create(self, control_zone_temperature_place_link_create: ControlZoneTemperaturePlaceLinkCreate) -> ControlZoneTemperaturePlaceLink:
        raise NotImplementedError
    
    @abstractmethod
    def get(self, hvac_widget_id: UUID, temperature_place_id: UUID) -> Optional[ControlZoneTemperaturePlaceLink]:
        raise NotImplementedError
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[ControlZoneTemperaturePlaceLink]:
        raise NotImplementedError
    
    @abstractmethod
    def delete(self, hvac_widget_id: UUID, temperature_place_id: UUID) -> None:
        raise NotImplementedError


class PostgresControlZoneTemperaturePlaceLinksRepository(ControlZoneTemperaturePlaceLinksRepository):

    def __init__(self, session: Session):
        self.session = session

    @final
    def create(self, control_zone_temperature_place_link_create: ControlZoneTemperaturePlaceLinkCreate) -> ControlZoneTemperaturePlaceLink:
        control_zone_temperature_place_link = ControlZoneTemperaturePlaceLinkModel(
            hvac_widget_id=control_zone_temperature_place_link_create.hvac_widget_id,
            temperature_place_id=control_zone_temperature_place_link_create.temperature_place_id,
            control_zone_temperature_place_type=control_zone_temperature_place_link_create.control_zone_temperature_place_type
        )
        try:
            self.session.add(control_zone_temperature_place_link)
            self.session.commit()
            self.session.refresh(control_zone_temperature_place_link)
            return ControlZoneTemperaturePlaceLink.model_validate(control_zone_temperature_place_link, from_attributes=True)
        except IntegrityError:
            raise ValueError('Control zone temperature place link already exists')
    
    @final
    def get(self, hvac_widget_id: UUID, temperature_place_id: UUID) -> Optional[ControlZoneTemperaturePlaceLink]:
        control_zone_temperature_place_link = self.session.query(ControlZoneTemperaturePlaceLinkModel).filter_by(hvac_widget_id=hvac_widget_id, temperature_place_id=temperature_place_id).first()
        if control_zone_temperature_place_link is None:
            return None
        return ControlZoneTemperaturePlaceLink.model_validate(control_zone_temperature_place_link, from_attributes=True)

    @final
    def filter_by(self, **kwargs) -> List[ControlZoneTemperaturePlaceLink]:
        control_zone_temperature_place_links = self.session.query(ControlZoneTemperaturePlaceLinkModel).filter_by(**kwargs).all()
        return [
            ControlZoneTemperaturePlaceLink.model_validate(control_zone_temperature_place_link, from_attributes=True)
            for control_zone_temperature_place_link in control_zone_temperature_place_links
        ]

    @final
    def delete(self, hvac_widget_id: UUID, temperature_place_id: UUID) -> None:
        control_zone_temperature_place_link = self.session.query(ControlZoneTemperaturePlaceLinkModel).filter_by(hvac_widget_id=hvac_widget_id, temperature_place_id=temperature_place_id).first()
        if control_zone_temperature_place_link is not None:
            self.session.delete(control_zone_temperature_place_link)
            self.session.commit()
