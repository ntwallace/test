from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import chain
from typing import Iterable, final
from typing_extensions import assert_never
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.electricity_monitoring.models.electric_sensor import ElectricSensor as ElectricSensorModel
from app.v1.hvac.models.thermostat import Thermostat as ThermostatModel
from app.v1.mesh_network.models.gateway import Gateway as GatewayModel
from app.v1.mesh_network.models.node import Node as NodeModel
from app.v1.temperature_monitoring.models.temperature_sensor import TemperatureSensor as TemperatureSensorModel


@dataclass
class LocationGateway:
    gateway_duid: str


@dataclass
class LocationDevice:
    device_duid: str
    location_id: UUID


class LocationDevicesRepository(ABC):
    @abstractmethod
    def get_devices(self, location_id: UUID) -> Iterable[LocationDevice]:
        ...

    @abstractmethod
    def get_gateways(self, location_id: UUID) -> Iterable[LocationGateway]:
        ...

    @abstractmethod
    def get_device_by_duid(self, device_duid: str) -> LocationDevice | None:
        ...


class PostgresLocationDevicesRepository(LocationDevicesRepository):
    def __init__(self, session: Session):
        self.session = session

    @final
    def get_devices(self, location_id: UUID) -> Iterable[LocationDevice]:
        temperature_sensors = self.session.query(TemperatureSensorModel).filter(TemperatureSensorModel.location_id == location_id).all()

        gateways = self.session.query(GatewayModel).filter(GatewayModel.location_id == location_id).all()
        nodes = self.session.query(NodeModel).filter(NodeModel.gateway_id.in_([x.gateway_id for x in gateways])).all()

        electric_sensors = self.session.query(ElectricSensorModel).filter(ElectricSensorModel.gateway_id.in_([x.gateway_id for x in gateways])).all()
        thermotats = self.session.query(ThermostatModel).filter(ThermostatModel.node_id.in_([node.node_id for node in nodes])).all()

        return [
            LocationDevice(
                device_duid=device.duid,
                location_id=location_id,
            )
            for device in chain[TemperatureSensorModel | ElectricSensorModel | ThermostatModel](
                temperature_sensors,
                electric_sensors,
                thermotats
            )
        ]

    @final
    def get_device_by_duid(self, device_duid: str) -> LocationDevice | None:
        temperature_sensor = self.session.query(TemperatureSensorModel).filter(TemperatureSensorModel.duid == device_duid).first()
        if temperature_sensor is not None:
            return LocationDevice(
                device_duid=device_duid,
                location_id=temperature_sensor.location_id,
            )

        electric_sensor = self.session.query(ElectricSensorModel).filter(ElectricSensorModel.duid == device_duid).first()
        if electric_sensor is not None:
            gateway = self.session.query(GatewayModel).filter(GatewayModel.gateway_id == electric_sensor.gateway_id).one()
            return LocationDevice(
                device_duid=device_duid,
                location_id=gateway.location_id,
            )
        thermostat = self.session.query(ThermostatModel).filter(TemperatureSensorModel.duid == device_duid).first()
        if thermostat is not None:
            if thermostat.node_id is None:
                # FIXME: This is here so we for sure do not forget that lorawan thermostats will have explicit gateway_id field
                # TODO: Remove after updating the code below to with new way to get gateway
                assert_never(thermostat.node_id)
            controller = self.session.query(NodeModel).filter(NodeModel.node_id == thermostat.node_id).one()
            gateway = self.session.query(GatewayModel).filter(GatewayModel.gateway_id == controller.gateway_id).one()
            return LocationDevice(
                device_duid=device_duid,
                location_id=gateway.location_id,
            )
        return None

    @final
    def get_gateways(self, location_id: UUID) -> Iterable[LocationGateway]:
        gateways = self.session.query(GatewayModel).filter(GatewayModel.location_id == location_id).all()
        return [
            LocationGateway(
                gateway_duid=gateway.duid,
            )
            for gateway in gateways
        ]
