from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.hvac.models.thermostat import Thermostat as ThermostatModel
from app.v1.hvac.schemas.thermostat import Thermostat, ThermostatCreate, ThermostatUpdate


class ThermostatsRepository(ABC):

    @abstractmethod
    def create(self, thermostat_create: ThermostatCreate) -> Thermostat:
        ...
    
    @abstractmethod
    def get(self, thermostat_id: UUID) -> Optional[Thermostat]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[Thermostat]:
        ...
    
    @abstractmethod
    def update(self, thermostat_update: ThermostatUpdate) -> Optional[Thermostat]:
        ...

    @abstractmethod
    def delete(self, thermostat_id: UUID) -> None:
        ...


class PostgresThermostatsRepository(ThermostatsRepository):

    def __init__(self, session: Session):
        self.session = session

    @final
    def create(self, thermostat_create: ThermostatCreate) -> Thermostat:
        try:
            thermostat = ThermostatModel(
                name=thermostat_create.name,
                duid=thermostat_create.duid,
                modbus_address=thermostat_create.modbus_address,
                model=thermostat_create.model,
                node_id=thermostat_create.node_id,
                hvac_zone_id=thermostat_create.hvac_zone_id,
                keypad_lockout=thermostat_create.keypad_lockout,
                fan_mode=thermostat_create.fan_mode
            )
            self.session.add(thermostat)
            self.session.commit()
            self.session.refresh(thermostat)
            return Thermostat.model_validate(thermostat, from_attributes=True)
        except IntegrityError:
            raise ValueError

    @final
    def get(self, thermostat_id: UUID) -> Optional[Thermostat]:
        thermostat = self.session.query(ThermostatModel).filter(ThermostatModel.thermostat_id == thermostat_id).first()
        if not thermostat:
            return None
        return Thermostat.model_validate(thermostat, from_attributes=True)

    @final
    def filter_by(self, **kwargs) -> List[Thermostat]:
        thermostats = self.session.query(ThermostatModel).filter_by(**kwargs).all()
        return [
            Thermostat.model_validate(thermostat, from_attributes=True)
            for thermostat in thermostats
        ]
    
    @final
    def update(self, thermostat_update: ThermostatUpdate) -> Optional[Thermostat]:
        thermostat = self.session.query(ThermostatModel).filter(ThermostatModel.thermostat_id == thermostat_update.thermostat_id).first()
        if thermostat is None:
            return None
        
        if thermostat_update.keypad_lockout is not None:
            thermostat.keypad_lockout = thermostat_update.keypad_lockout
        if thermostat_update.fan_mode is not None:
            thermostat.fan_mode = thermostat_update.fan_mode
            
        self.session.commit()
        self.session.refresh(thermostat)
        return Thermostat.model_validate(thermostat, from_attributes=True)


    @final
    def delete(self, thermostat_id: UUID) -> None:
        thermostat = self.session.query(ThermostatModel).filter(ThermostatModel.thermostat_id == thermostat_id).first()
        if thermostat:
            self.session.delete(thermostat)
            self.session.commit()
