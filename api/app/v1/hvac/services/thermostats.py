from typing import List
from uuid import UUID

from app.errors import NotFoundError
from app.v1.hvac.repositories.thermostats_repository import ThermostatsRepository
from app.v1.hvac.schemas.thermostat import Thermostat, ThermostatCreate, ThermostatModelEnum, ThermostatUpdate


class ThermostatsService:

    def __init__(self, thermostats_repository: ThermostatsRepository):
        self.thermostats_repository = thermostats_repository
    
    def create_thermostat(self, thermostat_create: ThermostatCreate) -> Thermostat:
        return self.thermostats_repository.create(thermostat_create)

    def get_thermostat_by_id(self, thermostat_id: UUID) -> Thermostat | None:
        return self.thermostats_repository.get(thermostat_id)

    def get_thermostat_by_attributes(self, name: str, duid: str, model: ThermostatModelEnum, node_id: UUID, hvac_zone_id: UUID) -> Thermostat | None:
        thermostats = self.thermostats_repository.filter_by(name=name, duid=duid, model=model, node_id=node_id, hvac_zone_id=hvac_zone_id)
        if len(thermostats) == 0:
            return None
        if len(thermostats) > 1:
            raise ValueError('Multiple thermostats found with the same attributes')
        return thermostats[0]

    def delete_thermostat(self, thermostat_id: UUID) -> None:
        self.thermostats_repository.delete(thermostat_id)

    def get_thermostat_for_hvac_zone(self, hvac_zone_id: UUID) -> Thermostat | None:
        thermostats = self.thermostats_repository.filter_by(hvac_zone_id=hvac_zone_id)
        if len(thermostats) == 0:
            return None
        if len(thermostats) > 1:
            raise ValueError('Multiple thermostats found for the same hvac zone')
        return thermostats[0]

    def update_thermostat(self, thermostat_update: ThermostatUpdate) -> Thermostat:
        thermostat = self.thermostats_repository.update(thermostat_update)
        if thermostat is None:
            raise NotFoundError('Thermostat not found')
        return thermostat
    
    def filter_by(self, **kwargs) -> List[Thermostat]:
        return self.thermostats_repository.filter_by(**kwargs)
