import argparse
from itertools import chain, groupby
import logging
import os
import re
from typing import Dict, List
from uuid import UUID, uuid4
import edgedb

from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.v1.appliances.models.appliance import Appliance
from app.v1.appliances.schemas.appliance_type import ApplianceSuperTypeEnum
from app.v1.auth.schemas.location_access_grant import LocationAccessGrant
from app.v1.auth.schemas.organization_access_grant import OrganizationAccessGrant
from app.v1.auth.models.user_location_access_grant import UserLocationAccessGrant
from app.v1.auth.models.user_organization_access_grant import UserOrganizationAccessGrant
from app.v1.electricity_dashboards.models.electricity_dashboard import ElectricityDashboard
from app.v1.electricity_monitoring.models.circuit import Circuit, CircuitTypeEnum
from app.v1.electricity_monitoring.models.clamp import Clamp, ClampPhaseEnum
from app.v1.electricity_monitoring.models.electric_panel import ElectricPanel
from app.v1.electricity_monitoring.models.electric_sensor import ElectricSensor
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanelTypeEnum
from app.v1.hvac.models.hvac_hold import HvacHold
from app.v1.hvac.models.hvac_schedule import HvacSchedule, HvacScheduleEvent
from app.v1.hvac.models.hvac_zone_equipment import HvacZoneEquipment
from app.v1.hvac.models.hvac_zone import HvacZone
from app.v1.hvac.models.thermostat import Thermostat, ThermostatModelEnum
from app.v1.hvac.schemas.hvac_schedule import HvacScheduleMode
from app.v1.hvac_dashboards.models.control_zone_hvac_widget import ControlZoneHvacWidget
from app.v1.hvac_dashboards.models.control_zone_temperature_place_link import ControlZoneTemperaturePlaceLink
from app.v1.hvac_dashboards.models.hvac_dashboard import HvacDashboard
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import ControlZoneTemperaturePlaceType, HvacFanMode
from app.v1.locations.models.location import Location
from app.v1.locations.models.location_electricity_price import LocationElectricityPrice
from app.v1.locations.models.location_operating_hours import LocationOperatingHours
from app.v1.locations.models.location_time_of_use_rate import LocationTimeOfUseRate
from app.v1.mesh_network.models.gateway import Gateway
from app.v1.mesh_network.models.node import Node, NodeTypeEnum
from app.v1.organizations.models.organization_feature_toggle import OrganizationFeatureToggle, OrganizationFeatureToggleEnum
from app.v1.organizations.models.organization import Organization
from app.v1.organizations.models.organization_user import OrganizationUser
from app.v1.schemas import DayOfWeek
from app.v1.temperature_dashboards.models.temperature_dashboard import TemperatureDashboard
from app.v1.temperature_dashboards.models.temeprature_unit_widget import ApplianceType, TemperatureUnitWidget
from app.v1.temperature_monitoring.models.temperature_range import TemperatureRange, TemperatureRangeWarningLevelEnum
from app.v1.temperature_monitoring.models.temperature_sensor import TemperatureSensor
from app.v1.temperature_monitoring.models.temperature_sensor_place import TemperatureSensorPlace
from app.v1.temperature_monitoring.models.temperature_sensor_place_alert import TemperatureSensorPlaceAlert, TemperatureSensorPlaceAlertType
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import TemperatureSensorPlaceType
from app.v1.users.models.user import User
from app.v1.electricity_dashboards.models.energy_consumption_breakdown_electric_widget import EnergyConsumptionBreakdownElectricWidget
from app.v1.electricity_dashboards.models.energy_load_curve_electric_widget import EnergyLoadCurveElectricWidget
from app.v1.electricity_dashboards.models.panel_system_health_electric_widget import PanelSystemHealthElectricWidget
from app.v3_adapter.operating_range_notification_settings.models import OperatingRangeNotificationSettings

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

TEST_EDGEDB_CONNECTION = True
TEST_POSTGRES_CONNECTION = True

DRY_RUN = os.environ['DRY_RUN'].lower() == 'true' if os.environ.get('DRY_RUN', None) is not None else True
FUNCTION_LOG_FILTER = [
]

EDGEDB_HOST = os.environ['MIGRATION_EDGEDB_HOST']
EDGEDB_PORT = os.environ['MIGRATION_EDGEDB_PORT']
EDGEDB_USER = os.environ['MIGRATION_EDGEDB_USER']
EDGEDB_PASS = os.environ['MIGRATION_EDGEDB_PASS']
EDGEDB_NAME = os.environ['MIGRATION_EDGEDB_NAME']
EDGEDB_CONNECTION_URI = f'edgedb://{EDGEDB_USER}:{EDGEDB_PASS}@{EDGEDB_HOST}:{EDGEDB_PORT}/{EDGEDB_NAME}'

POWERX_DATABASE_HOST = os.environ['MIGRATION_POWERX_DATABASE_HOST']
POWERX_DATABASE_PORT = os.environ['MIGRATION_POWERX_DATABASE_PORT']
POWERX_DATABASE_USER = os.environ['MIGRATION_POWERX_DATABASE_USER']
POWERX_DATABASE_PASSWORD = os.environ['MIGRATION_POWERX_DATABASE_PASSWORD']
POWERX_DATABASE_NAME = os.environ['MIGRATION_POWERX_DATABASE_NAME']
POWERX_DATABASE_URL = f"postgresql://{POWERX_DATABASE_USER}:{POWERX_DATABASE_PASSWORD}@{POWERX_DATABASE_HOST}:{POWERX_DATABASE_PORT}/{POWERX_DATABASE_NAME}"


edgedb_client = edgedb.create_client(
    dsn=EDGEDB_CONNECTION_URI,
    tls_security='insecure'
).with_state(edgedb.State(
    config={
        'allow_user_specified_id': True,
        'apply_access_policies': False,
    }
))

if TEST_EDGEDB_CONNECTION:
    logger.info('Testing EdgeDB connection')
    for tx in edgedb_client.transaction():
        with tx:
            response = tx.execute('SELECT 1')
            logger.info('EdgeDB connection test successful')

engine = create_engine(
    POWERX_DATABASE_URL
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
postgres_session = SessionLocal()

if TEST_POSTGRES_CONNECTION:
    logger.info('Testing PostgreSQL connection')
    postgres_session.execute(text('SELECT 1'))
    logger.info('PostgreSQL connection test successful')


def log_returned_data(func):
    def wrapper(*args, **kwargs):
        logger.info('')
        logger.info(f'{func.__name__}:')
        result = func(*args, **kwargs)

        if len(FUNCTION_LOG_FILTER) > 0 and func.__name__ not in FUNCTION_LOG_FILTER:
            return result

        if isinstance(result, list):
            result_list = [
                {
                    key: value
                    for key, value in item.__dict__.items()
                    if key != '_sa_instance_state'
                }
                for item in result
            ]
            log_str = '\n    '.join([str(item) for item in result_list])
            logger.info(f"\n    {log_str}")
        else:
            logger.info(
                {
                    key: value
                    for key, value in result.__dict__.items()
                    if key != '_sa_instance_state'
                }
            )
        return result

    return wrapper

# Organization data
@log_returned_data
def get_organization(organization_id: UUID) -> Organization:
    for tx in edgedb_client.transaction():
        with tx:
            organizations = tx.query(
                '''
                SELECT Organization {
                    id,
                    name,
                    logo_path,
                    created_at,
                    modified_at
                }
                FILTER .id = <uuid>$organization_id
                ''',
                organization_id=organization_id
            )
            if len(organizations) == 0:
                raise ValueError('Organization not found')
            if len(organizations) > 1:
                raise ValueError('Multiple organizations found')
            organization = organizations[0]
            return Organization(
                organization_id=organization.id,
                name=organization.name,
                logo_url=organization.logo_path,
                created_at=organization.created_at,
                updated_at=organization.modified_at
            )

@log_returned_data
def get_organization_feature_toggles(organization_id: UUID) -> List[OrganizationFeatureToggle]:
    for tx in edgedb_client.transaction():
        with tx:
            organization = tx.query_single(
                '''
                SELECT Organization {
                    id,
                    feature_toggles,
                    created_at
                }
                FILTER .id = <uuid>$organization_id
                LIMIT 1
                ''',
                organization_id=organization_id
            )
            if organization is None:
                raise ValueError('Organization not found')
            feature_toggles_str = organization.feature_toggles
            return [
                OrganizationFeatureToggle(
                    organization_feature_toggle_id=uuid4(),
                    organization_id=organization_id,
                    organization_feature_toggle=OrganizationFeatureToggleEnum.from_str(feature_toggle_str),
                    is_enabled=True,
                    created_at=organization.created_at,
                    updated_at=organization.created_at
                )
                for feature_toggle_str in feature_toggles_str 
            ]


# Organization users data

@log_returned_data
def get_users(organization_id: UUID) -> List[User]:
    for tx in edgedb_client.transaction():
        with tx:
            organization = tx.query_single(
                '''
                SELECT Organization {
                    accounts: {
                        id,
                        email,
                        given_name,
                        family_name,
                        phone_number,
                        password,
                        created_at,
                        modified_at
                    }
                }
                FILTER .id = <uuid>$organization_id
                ''',
                organization_id=organization_id
            )
            return [
                User(
                    user_id=account.id,
                    email=account.email,
                    password_hash=account.password,
                    first_name=account.given_name,
                    last_name=account.family_name,
                    created_at=account.created_at,
                    updated_at=account.modified_at
                )
                for account in organization.accounts
            ]

@log_returned_data
def get_organization_owner_user(organization_id: UUID) -> User:
    for tx in edgedb_client.transaction():
        with tx:
            organization = tx.query_single(
                '''
                SELECT Organization {
                    owner: {
                        id,
                        email,
                        given_name,
                        family_name,
                        password,
                        created_at,
                        modified_at
                    }
                }
                FILTER .id = <uuid>$organization_id
                ''',
                organization_id=organization_id
            )
            return User(
                user_id=organization.owner.id,
                email=organization.owner.email,
                password_hash=organization.owner.password if organization.owner.password.lower() != 'unset' else None,
                first_name=organization.owner.given_name,
                last_name=organization.owner.family_name,
                created_at=organization.owner.created_at,
                updated_at=organization.owner.modified_at
            )


# Locations data

@log_returned_data
def get_locations(organization_id: UUID) -> List[Location]:
    for tx in edgedb_client.transaction():
        with tx:
            locations = tx.query(
                '''
                SELECT Location {
                    id,
                    address,
                    city,
                    country,
                    created_at,
                    latitude,
                    longitude,
                    modified_at,
                    name,
                    state,
                    timezone,
                    zip
                }
                FILTER .organization.id = <uuid>$organization_id
                ''',
                organization_id=organization_id
            )
            return [
                Location(
                    location_id=location.id,
                    name=location.name,
                    address=location.address,
                    city=location.city,
                    state=location.state,
                    zip_code=location.zip,
                    country=location.country,
                    latitude=location.latitude,
                    longitude=location.longitude,
                    timezone=location.timezone,
                    organization_id=organization_id,
                    created_at=location.created_at,
                    updated_at=location.modified_at
                )
                for location in locations
            ]


# Core data

@log_returned_data
def get_appliances(location_id: UUID) -> List[Appliance]:
    for tx in edgedb_client.transaction():
        with tx:
            appliances = tx.query(
                '''
                SELECT TemperatureUnit {
                    id,
                    name,
                    appliance,
                    created_at,
                    modified_at,
                    temperature_place: {
                        id
                    }
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return [
                Appliance(
                    appliance_id=appliance.id,
                    appliance_super_type=ApplianceSuperTypeEnum(appliance.appliance.value.lower()),
                    serial=None,
                    appliance_type_id=None,
                    circuit_id=None,
                    temperature_sensor_place_id=appliance.temperature_place.id,
                    location_id=location_id,
                    created_at=appliance.created_at,
                    updated_at=appliance.modified_at
                )
                for appliance in appliances
            ]

@log_returned_data
def get_circuits(location_id: UUID) -> List[Circuit]:
    for tx in edgedb_client.transaction():
        with tx:
            branch_circuits = tx.query(
                '''
                SELECT BranchCircuit {
                    id,
                    name,
                    tags,
                    created_at,
                    modified_at,
                    panels: {
                        id
                    }
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            mains = tx.query(
                '''
                SELECT Mains {
                    id,
                    name,
                    tags,
                    created_at,
                    modified_at,
                    panel: {
                        id
                    }
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            neutrals = tx.query(
                '''
                SELECT Neutral {
                    id,
                    name,
                    tags,
                    created_at,
                    modified_at,
                    panel: {
                        id
                    }
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return list(chain(
                [
                    Circuit(
                        circuit_id=branch_circuit.id,
                        name=branch_circuit.name,
                        type=CircuitTypeEnum.branch,
                        electric_panel_id=branch_circuit.panels[0].id,
                        created_at=branch_circuit.created_at,
                        updated_at=branch_circuit.modified_at
                    )
                    for branch_circuit in branch_circuits
                ],
                [
                    Circuit(
                        circuit_id=main.id,
                        name=main.name,
                        type=CircuitTypeEnum.main,
                        electric_panel_id=main.panel.id,
                        created_at=main.created_at,
                        updated_at=main.modified_at
                    )
                    for main in mains
                ],
                [
                    Circuit(
                        circuit_id=neutral.id,
                        name=neutral.name,
                        type=CircuitTypeEnum.neutral,
                        electric_panel_id=neutral.panel.id,
                        created_at=neutral.created_at,
                        updated_at=neutral.modified_at
                    )
                    for neutral in neutrals
                ]
            ))

@log_returned_data
def get_clamps(location_id: UUID) -> List[Clamp]:
    for tx in edgedb_client.transaction():
        with tx:
            clamps = tx.query(
                '''
                SELECT Clamp {
                    id,
                    circuit_id,
                    port_name,
                    port_pin,
                    amperage_rating,
                    created_at,
                    modified_at,
                    name,
                    sensor_id,
                    phase: {
                        id,
                        name,
                        voltage_field
                    },
                    sensor: {
                        id
                    }
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return [
                Clamp(
                    clamp_id=clamp.id,
                    name=clamp.name,
                    port_name=clamp.port_name.lower(),
                    port_pin=clamp.port_pin,
                    amperage_rating=int(re.findall(r'\d+', clamp.amperage_rating)[0]),
                    phase=ClampPhaseEnum(clamp.phase.name),
                    circuit_id=clamp.circuit_id,
                    electric_sensor_id=clamp.sensor_id,
                    created_at=clamp.created_at,
                    updated_at=clamp.modified_at
                )
                for clamp in clamps
                if clamp.phase is not None
            ]

@log_returned_data
def get_electric_sensors(location_id: UUID) -> List[ElectricSensor]:
    for tx in edgedb_client.transaction():
        with tx:
            electric_sensors = tx.query(
                '''
                SELECT ElectricSensor {
                    id,
                    name,
                    duid,
                    tags,
                    ports,
                    created_at,
                    modified_at,
                    panel: {
                        id
                    },
                    hub: {
                        id
                    }
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return [
                ElectricSensor(
                    electric_sensor_id=electric_sensor.id,
                    name=electric_sensor.name,
                    duid=electric_sensor.duid,
                    port_count=electric_sensor.ports,
                    electric_panel_id=electric_sensor.panel.id,
                    gateway_id=electric_sensor.hub.id,
                    a_breaker_num=0,
                    b_breaker_num=0,
                    c_breaker_num=0,
                    created_at=electric_sensor.created_at,
                    updated_at=electric_sensor.modified_at
                )
                for electric_sensor in electric_sensors
            ]

@log_returned_data
def get_electric_panels(location_id: UUID) -> List[ElectricPanel]:
    for tx in edgedb_client.transaction():
        with tx:
            electric_panels = tx.query(
                '''
                SELECT ElectricPanel {
                    id,
                    name,
                    parent_id,
                    created_at,
                    modified_at
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return [
                ElectricPanel(
                    electric_panel_id=electric_panel.id,
                    name=electric_panel.name,
                    panel_type=ElectricPanelTypeEnum.mdp if electric_panel.parent_id is None else ElectricPanelTypeEnum.sub,
                    location_id=location_id,
                    breaker_count=None,
                    parent_electric_panel_id=electric_panel.parent_id if electric_panel.parent_id is not None else None,
                    created_at=electric_panel.created_at,
                    updated_at=electric_panel.modified_at
                )
                for electric_panel in electric_panels
            ]

@log_returned_data
def get_gateways(location_id: UUID) -> List[Gateway]:
    for tx in edgedb_client.transaction():
        with tx:
            hubs = tx.query(
                '''
                SELECT SyncromeshHub {
                    id,
                    name,
                    duid,
                    tags,
                    created_at,
                    modified_at
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return [
                Gateway(
                    gateway_id=hub.id,
                    name=hub.name,
                    duid=hub.duid,
                    created_at=hub.created_at,
                    updated_at=hub.modified_at,
                    location_id=location_id
                )
                for hub in hubs
            ]

@log_returned_data
def get_hvac_zone_equipment(location_id: UUID) -> List[HvacZoneEquipment]:
    ...

@log_returned_data
def get_hvac_zone_temperature_sensors(location_id: UUID) -> List[TemperatureSensor]:
    ...

@log_returned_data
def get_hvac_zones(location_id: UUID) -> List[HvacZone]:
    for tx in edgedb_client.transaction():
        with tx:
            control_zone_widgets = tx.query(
                '''
                SELECT ControlZoneWidget {
                    id,
                    name,
                    created_at,
                    modified_at
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return [
                HvacZone(
                    hvac_zone_id=uuid4(),
                    name=control_zone_widget.name,
                    location_id=location_id,
                    created_at=control_zone_widget.created_at,
                    updated_at=control_zone_widget.modified_at
                )
                for control_zone_widget in control_zone_widgets
            ]


@log_returned_data
def get_location_electricity_prices(location_id: UUID) -> List[LocationElectricityPrice]:
    for tx in edgedb_client.transaction():
        with tx:
            electricity_prices = tx.query(
                '''
                SELECT ElectricityPrice {
                    id,
                    comment,
                    price_per_kwh,
                    effective_from,
                    effective_to,
                    created_at,
                    modified_at
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return [
                LocationElectricityPrice(
                    location_electricity_price_id=electricity_price.id,
                    location_id=location_id,
                    comment=electricity_price.comment,
                    price_per_kwh=electricity_price.price_per_kwh,
                    started_at=electricity_price.effective_from,
                    ended_at=electricity_price.effective_to,
                    created_at=electricity_price.created_at,
                    updated_at=electricity_price.modified_at
                )
                for electricity_price in electricity_prices
            ]

@log_returned_data
def get_location_operating_hours(location_id: UUID) -> List[LocationOperatingHours]:
    for tx in edgedb_client.transaction():
        with tx:
            operating_hours = tx.query_single(
                '''
                SELECT OperatingHoursSettings {
                    id,
                    monday,
                    tuesday,
                    wednesday,
                    thursday,
                    friday,
                    saturday,
                    sunday,
                    created_at,
                    modified_at
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            if operating_hours is None:
                return []
            operating_hours_list: List[LocationOperatingHours] = []
            for day_of_week in DayOfWeek:
                operating_hours_tuple = getattr(operating_hours, day_of_week.value)
                operating_hours_list.append(
                    LocationOperatingHours(
                        location_id=location_id,
                        day_of_week=day_of_week,
                        is_open=True if operating_hours_tuple is not None else False,
                        work_start_time=operating_hours_tuple[0] if operating_hours_tuple is not None else None,
                        open_time=operating_hours_tuple[1] if operating_hours_tuple is not None else None,
                        close_time=operating_hours_tuple[2] if operating_hours_tuple is not None else None,
                        work_end_time=operating_hours_tuple[3] if operating_hours_tuple is not None else None,
                        created_at=operating_hours.created_at,
                        updated_at=operating_hours.modified_at
                    )
                )
            return operating_hours_list

@log_returned_data
def get_location_time_of_use_rates(location_id: UUID) -> List[LocationTimeOfUseRate]:
    for tx in edgedb_client.transaction():
        with tx:
            time_of_use_rates = tx.query(
                '''
                SELECT TimeOfUseRate {
                    id,
                    days_of_week,
                    archived,
                    comment,
                    price_per_kwh,
                    day_seconds_from,
                    day_seconds_to,
                    effective_from,
                    effective_to,
                    recur_yearly,
                    created_at,
                    modified_at,
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return [
                LocationTimeOfUseRate(
                    location_id=location_id,
                    days_of_week=[DayOfWeek(day_of_week.value.lower()) for day_of_week in time_of_use_rate.days_of_week],
                    is_active=not time_of_use_rate.archived,
                    comment=time_of_use_rate.comment,
                    price_per_kwh=time_of_use_rate.price_per_kwh,
                    day_started_at_seconds=time_of_use_rate.day_seconds_from,
                    day_ended_at_seconds=time_of_use_rate.day_seconds_to,
                    start_at=time_of_use_rate.effective_from,
                    end_at=time_of_use_rate.effective_to,
                    recurs_yearly=time_of_use_rate.recur_yearly,
                    created_at=time_of_use_rate.created_at,
                    updated_at=time_of_use_rate.modified_at
                )
                for time_of_use_rate in time_of_use_rates
            ]

@log_returned_data
def get_nodes(location_id: UUID) -> List[Node]:
    for tx in edgedb_client.transaction():
        with tx:
            modbus_nodes = tx.query(
                '''
                SELECT SyncromeshModbusNode {
                    id,
                    name,
                    duid,
                    tags,
                    created_at,
                    modified_at,
                    hub: {
                        id
                    },
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            standard_nodes = tx.query(
                '''
                SELECT SyncromeshStandardNode {
                    id,
                    name,
                    duid,
                    tags,
                    created_at,
                    modified_at,
                    hub: {
                        id
                    },
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            nodes = list(chain(
                [
                    Node(
                        node_id=modbus_node.id,
                        name=modbus_node.name,
                        duid=modbus_node.duid,
                        gateway_id=modbus_node.hub.id,
                        type=NodeTypeEnum.MODBUS,
                        created_at=modbus_node.created_at,
                        updated_at=modbus_node.modified_at
                    )
                    for modbus_node in modbus_nodes
                ],
                [
                    Node(
                        node_id=standard_node.id,
                        name=standard_node.name,
                        duid=standard_node.duid,
                        gateway_id=standard_node.hub.id,
                        type=NodeTypeEnum.STANDARD,
                        created_at=standard_node.created_at,
                        updated_at=standard_node.modified_at
                    )
                    for standard_node in standard_nodes
                ]
            ))
            return nodes

@log_returned_data
def get_operating_range_notification_settings(organization_id: UUID) -> List[OperatingRangeNotificationSettings]:
    for tx in edgedb_client.transaction():
        with tx:
            operating_range_notification_settings = tx.query(
                '''
                SELECT OperatingRangeNotificationSettings {
                    id,
                    allows_emails,
                    created_at,
                    modified_at,
                    account: {
                        id
                    },
                    location: {
                        id
                    }
                }
                FILTER .organization.id = <uuid>$organization_id
                ''',
                organization_id=organization_id
            )
            return [
                OperatingRangeNotificationSettings(
                    operating_range_notification_settings_id=notification_setting.id,
                    location_id=notification_setting.location.id,
                    user_id=notification_setting.account.id,
                    allow_emails=notification_setting.allows_emails,
                    created_at=notification_setting.created_at,
                    updated_at=notification_setting.modified_at
                )
                for notification_setting in operating_range_notification_settings
            ]

@log_returned_data
def get_temperature_ranges(location_id: UUID) -> List[TemperatureRange]:
    for tx in edgedb_client.transaction():
        with tx:
            temperature_ranges = tx.query(
                '''
                SELECT TemperatureRange {
                    id,
                    high_c,
                    low_c,
                    warning_level,
                    created_at,
                    modified_at,
                    temperature_place: {
                        id
                    }
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return [
                TemperatureRange(
                    temperature_range_id=temperature_range.id,
                    high_degrees_celcius=temperature_range.high_c,
                    low_degrees_celcius=temperature_range.low_c,
                    warning_level=TemperatureRangeWarningLevelEnum(temperature_range.warning_level.value.lower()),
                    temperature_sensor_place_id=temperature_range.temperature_place.id,
                    created_at=temperature_range.created_at,
                    updated_at=temperature_range.modified_at
                )
                for temperature_range in temperature_ranges
            ]

@log_returned_data
def get_temperature_sensor_place_alerts(location_id: UUID) -> List[TemperatureSensorPlaceAlert]:
    for tx in edgedb_client.transaction():
        with tx:
            temperature_sensor_place_alerts = tx.query(
                '''
                SELECT OutOfNormalOperatingRange {
                    id,
                    threshold_type,
                    threshold_temperature_c,
                    threshold_window_s,
                    reporter_temperature_c,
                    started,
                    resolved,
                    created_at,
                    modified_at,
                    temperature_unit: {
                        temperature_place: {
                            id
                        }
                    }
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return [
                TemperatureSensorPlaceAlert(
                    temperature_sensor_place_alert_id=temperature_sensor_place_alert.id,
                    temperature_sensor_place_id=temperature_sensor_place_alert.temperature_unit.temperature_place.id,
                    alert_type=TemperatureSensorPlaceAlertType.ABOVE_NORMAL_OPERATING_RANGE if temperature_sensor_place_alert.threshold_type.value.lower() == 'high' else TemperatureSensorPlaceAlertType.BELOW_NORMAL_OPERATING_RANGE,
                    threshold_temperature_c=temperature_sensor_place_alert.threshold_temperature_c,
                    threshold_window_seconds=temperature_sensor_place_alert.threshold_window_s,
                    reporter_temperature_c=temperature_sensor_place_alert.reporter_temperature_c,
                    started_at=temperature_sensor_place_alert.started,
                    ended_at=temperature_sensor_place_alert.resolved,
                    created_at=temperature_sensor_place_alert.created_at,
                    updated_at=temperature_sensor_place_alert.modified_at
                )
                for temperature_sensor_place_alert in temperature_sensor_place_alerts
            ]

@log_returned_data
def get_temperature_senors_places(location_id: UUID) -> List[TemperatureSensorPlace]:
    for tx in edgedb_client.transaction():
        with tx:
            temperature_sensor_places = tx.query(
                '''
                SELECT TemperaturePlace {
                    id,
                    name,
                    tags,
                    created_at,
                    modified_at,
                    temperature_sensor_link: {
                        sensor: {
                            id
                        }
                    },
                    temperature_unit := .<temperature_place[is TemperatureUnit] { id }
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return [
                TemperatureSensorPlace(
                    temperature_sensor_place_id=temperature_sensor_place.id,
                    location_id=location_id,
                    name=temperature_sensor_place.name,
                    temperature_sensor_place_type=TemperatureSensorPlaceType.APPLIANCE if len(temperature_sensor_place.temperature_unit) > 0 else TemperatureSensorPlaceType.ZONE,
                    temperature_sensor_id=temperature_sensor_place.temperature_sensor_link.sensor.id if temperature_sensor_place.temperature_sensor_link is not None and temperature_sensor_place.temperature_sensor_link.sensor is not None else None,
                    created_at=temperature_sensor_place.created_at,
                    updated_at=temperature_sensor_place.modified_at
                )
                for temperature_sensor_place in temperature_sensor_places
            ]

@log_returned_data
def get_temperature_sensors(location_id: UUID) -> List[TemperatureSensor]:
    for tx in edgedb_client.transaction():
        with tx:
            temperature_sensors = tx.query(
                '''
                SELECT SyncromeshTemperatureSensor {
                    id,
                    name,
                    duid,
                    tags,
                    created_at,
                    modified_at,
                    hub: {
                        id
                    }
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return [
                TemperatureSensor(
                    temperature_sensor_id=temperature_sensor.id,
                    name=temperature_sensor.name,
                    duid=temperature_sensor.duid,
                    make=None,
                    model=None,
                    gateway_id=temperature_sensor.hub.id,
                    location_id=location_id,
                    created_at=temperature_sensor.created_at,
                    updated_at=temperature_sensor.modified_at
                )
                for temperature_sensor in temperature_sensors
            ]

@log_returned_data
def get_thermostats(location_id: UUID, control_zone_hvac_widgets: List[ControlZoneHvacWidget]) -> List[Thermostat]:
    control_zone_hvac_widgets_map: Dict[UUID, ControlZoneHvacWidget] = {
        control_zone_hvac_widget.hvac_widget_id: control_zone_hvac_widget
        for control_zone_hvac_widget in control_zone_hvac_widgets
    }
    for tx in edgedb_client.transaction():
        with tx:
            control_zone_hvac_widgets = tx.query(
                '''
                SELECT ControlZoneWidget {
                    id,
                    thermostat: {
                        id,
                        name,
                        duid,
                        fan_mode,
                        keypad_lockout,
                        modbus_address,
                        model,
                        created_at,
                        modified_at,
                        controller: {
                            id
                        }
                    }
                }
                FILTER .location.id = <uuid>$location_id
                ''',
                location_id=location_id
            )
            return [
                Thermostat(
                    thermostat_id=control_zone_widget.thermostat.id,
                    name=control_zone_widget.thermostat.name,
                    duid=control_zone_widget.thermostat.duid,
                    modbus_address=control_zone_widget.thermostat.modbus_address,
                    model=ThermostatModelEnum.v1,
                    node_id=control_zone_widget.thermostat.controller.id,
                    hvac_zone_id=control_zone_hvac_widgets_map[control_zone_widget.id].hvac_zone_id,
                    keypad_lockout=control_zone_widget.thermostat.keypad_lockout,
                    fan_mode=control_zone_widget.thermostat.fan_mode,
                    created_at=control_zone_widget.thermostat.created_at,
                    updated_at=control_zone_widget.thermostat.modified_at
                )
                for control_zone_widget in control_zone_hvac_widgets
                if control_zone_widget.thermostat is not None
            ]

@log_returned_data
def get_user_access_roles(location_id: UUID):
    ...

@log_returned_data
def get_user_access_scopes(location_id: UUID):
    ...

@log_returned_data
def get_user_location_access_grants(organization_id: UUID) -> List[UserLocationAccessGrant]:
    for tx in edgedb_client.transaction():
        with tx:
            user_location_access_grants = tx.query(
                '''
                SELECT Permission {
                    id,
                    grants,
                    created_at,
                    modified_at,
                    account: {
                        id
                    },
                    target[is Location]

                }
                FILTER .organization.id = <uuid>$organization_id
                ''',
                organization_id=organization_id
            )
            return [
                UserLocationAccessGrant(
                    user_id=user_location_access_grant.account.id,
                    location_id=user_location_access_grant.target.id,
                    location_access_grant=LocationAccessGrant(grant.value),
                    created_at=user_location_access_grant.created_at,
                )
                for user_location_access_grant in user_location_access_grants
                for grant in user_location_access_grant.grants
                if user_location_access_grant.target is not None
            ]

@log_returned_data
def get_user_organization_access_grants(organization_id: UUID) -> List[UserOrganizationAccessGrant]:
    for tx in edgedb_client.transaction():
        with tx:
            user_location_access_grants = tx.query(
                '''
                SELECT Permission {
                    id,
                    grants,
                    created_at,
                    modified_at,
                    account: {
                        id
                    },
                    target[is Organization]

                }
                FILTER .organization.id = <uuid>$organization_id
                ''',
                organization_id=organization_id
            )
            return [
                UserOrganizationAccessGrant(
                    user_id=user_location_access_grant.account.id,
                    organization_id=user_location_access_grant.target.id,
                    organization_access_grant=OrganizationAccessGrant(grant.value),
                    created_at=user_location_access_grant.created_at,
                )
                for user_location_access_grant in user_location_access_grants
                for grant in user_location_access_grant.grants
                if user_location_access_grant.target is not None
            ]


###########
# Dashboard specific
###########

# HVAC dashboard data

@log_returned_data
def get_hvac_dashboards(organization_id: UUID) -> List[HvacDashboard]:
    for tx in edgedb_client.transaction():
        with tx:
            hvac_dashboards = tx.query(
                '''
                SELECT HvacDashboard {
                    id,
                    name,
                    dashboard_type,
                    created_at,
                    modified_at,
                    location: {
                        id
                    }
                }
                FILTER .organization.id = <uuid>$organization_id
                ''',
                organization_id=organization_id
            )
            return [
                HvacDashboard(
                    hvac_dashboard_id=hvac_dashboard.id,
                    name=hvac_dashboard.name,
                    location_id=hvac_dashboard.location.id,
                    created_at=hvac_dashboard.created_at,
                    updated_at=hvac_dashboard.modified_at
                )
                for hvac_dashboard in hvac_dashboards
            ]

@log_returned_data
def get_control_zone_hvac_widgets_for_dashboard(hvac_dashboard_id: UUID, hvac_zones: List[HvacZone]) -> List[ControlZoneHvacWidget]:
    location_hvac_zone_map: Dict[UUID, Dict[str, HvacZone]] = {
        location_id: {
            zone.name.lower(): zone
            for zone in location_hvac_zones
        }
        for (location_id, location_hvac_zones) in groupby(hvac_zones, lambda zone: zone.location_id)
    }
    for tx in edgedb_client.transaction():
        with tx:
            widgets = tx.query(
                '''
                SELECT ControlZoneWidget {
                    id,
                    name,
                    widget_type,
                    created_at,
                    modified_at,
                    monday_schedule: {
                        id,
                    },
                    tuesday_schedule: {
                        id,
                    },
                    wednesday_schedule: {
                        id,
                    },
                    thursday_schedule: {
                        id,
                    },
                    friday_schedule: {
                        id,
                    },
                    saturday_schedule: {
                        id,
                    },
                    sunday_schedule: {
                        id,
                    },
                    thermostat: {
                        id,
                    },
                    input_ducts: {
                        id,
                        created_at,
                        modified_at
                    },
                    output_ducts: {
                        id,
                        created_at,
                        modified_at
                    },
                    room_temperatures: {
                        id,
                        created_at,
                        modified_at
                    },
                    location: {
                        id
                    }
                }
                FILTER .dashboard.id = <uuid>$hvac_dashboard_id
                ''',
                hvac_dashboard_id=hvac_dashboard_id
            )
            control_zone_hvac_widgets: List[ControlZoneHvacWidget] = []
            for widget in widgets:
                hvac_zone_for_widget = location_hvac_zone_map.get(widget.location.id, {}).get(widget.name.lower())
                hvac_zone_id = getattr(hvac_zone_for_widget, 'hvac_zone_id') if hvac_zone_for_widget is not None else None
                control_zone_hvac_widget = ControlZoneHvacWidget(
                    hvac_widget_id=widget.id,
                    hvac_zone_id=hvac_zone_id,
                    name=widget.name,
                    hvac_dashboard_id=hvac_dashboard_id,
                    created_at=widget.created_at,
                    updated_at=widget.modified_at,
                    monday_schedule_id=widget.monday_schedule.id if widget.monday_schedule else None,
                    tuesday_schedule_id=widget.tuesday_schedule.id if widget.tuesday_schedule else None,
                    wednesday_schedule_id=widget.wednesday_schedule.id if widget.wednesday_schedule else None,
                    thursday_schedule_id=widget.thursday_schedule.id if widget.thursday_schedule else None,
                    friday_schedule_id=widget.friday_schedule.id if widget.friday_schedule else None,
                    saturday_schedule_id=widget.saturday_schedule.id if widget.saturday_schedule else None,
                    sunday_schedule_id=widget.sunday_schedule.id if widget.sunday_schedule else None
                )
                control_zone_hvac_widget.temperature_place_links = list(chain(
                    [
                        ControlZoneTemperaturePlaceLink(
                            hvac_widget_id=widget.id,
                            temperature_place_id=input_duct.id,
                            control_zone_temperature_place_type=ControlZoneTemperaturePlaceType.INPUT_DUCT,
                            created_at=input_duct.created_at,
                            updated_at=input_duct.modified_at
                        )
                        for input_duct in widget.input_ducts
                    ],
                    [
                        ControlZoneTemperaturePlaceLink(
                            hvac_widget_id=widget.id,
                            temperature_place_id=output_duct.id,
                            control_zone_temperature_place_type=ControlZoneTemperaturePlaceType.OUTPUT_DUCT,
                            created_at=output_duct.created_at,
                            updated_at=output_duct.modified_at
                        )
                        for output_duct in widget.output_ducts
                    ],
                    [
                        ControlZoneTemperaturePlaceLink(
                            hvac_widget_id=widget.id,
                            temperature_place_id=room_temeperature.id,
                            control_zone_temperature_place_type=ControlZoneTemperaturePlaceType.ROOM,
                            created_at=room_temeperature.created_at,
                            updated_at=room_temeperature.modified_at
                        )
                        for room_temeperature in widget.room_temperatures
                    ]
                ))
                control_zone_hvac_widgets.append(control_zone_hvac_widget)

            return control_zone_hvac_widgets

@log_returned_data
def get_hvac_schedules(organization_id: UUID) -> List[HvacSchedule]:
    for tx in edgedb_client.transaction():
        with tx:
            hvac_schedules = tx.query(
                '''
                SELECT HvacSchedule {
                    id,
                    name,
                    created_at,
                    modified_at,
                    events,
                    location: {
                        id
                    }
                }
                FILTER .organization.id = <uuid>$organization_id
                ''',
                organization_id=organization_id
            )

            hvac_schedule_events: List[HvacScheduleEvent] = [
                HvacScheduleEvent(
                    hvac_schedule_id=hvac_schedule.id,
                    hvac_schedule_event_id=uuid4(),
                    mode=HvacScheduleMode(event[0].value.lower()),
                    time=event[1],
                    set_point_c=event[2],
                    set_point_heating_c=event[3],
                    set_point_cooling_c=event[4],
                    created_at=hvac_schedule.created_at,
                    updated_at=hvac_schedule.modified_at,
                )
                for hvac_schedule in hvac_schedules
                for event in hvac_schedule.events
            ]
        
            schedule_events_map: Dict[UUID, List[HvacScheduleEvent]] = {
                str(hvac_schedule_id): list(schedules_hvac_schedule_events)
                for hvac_schedule_id, schedules_hvac_schedule_events in groupby(
                    hvac_schedule_events,
                    key=lambda event: event.hvac_schedule_id
                )
            }
            
            return [
                HvacSchedule(
                    hvac_schedule_id=hvac_schedule.id,
                    location_id=hvac_schedule.location.id,
                    name=hvac_schedule.name,
                    events=schedule_events_map[str(hvac_schedule.id)] if str(hvac_schedule.id) in schedule_events_map is not None else [],
                    created_at=hvac_schedule.created_at,
                    updated_at=hvac_schedule.modified_at
                )
                for hvac_schedule in hvac_schedules
            ]

@log_returned_data
def get_hvac_holds_for_organization(organization_id: UUID) -> List[HvacHold]:
    for tx in edgedb_client.transaction():
        with tx:
            widgets = tx.query(
                '''
                SELECT ControlZoneWidget {
                    id,
                    hvac_hold: {
                        id,
                        mode,
                        author,
                        fan_mode,
                        set_point,
                        set_point_auto,
                        expire_at_actual,
                        expire_at_estimated,
                        created_at,
                        modified_at,
                    },
                    thermostat: {
                        id
                    }
                }
                FILTER .organization.id = <uuid>$organization_id
                ''',
                organization_id=organization_id
            )
            return [
                HvacHold(
                    hvac_hold_id=widget.hvac_hold.id,
                    control_zone_hvac_widget_id=widget.id,
                    mode=HvacScheduleMode(widget.hvac_hold.mode.value.lower()),
                    fan_mode=HvacFanMode(widget.hvac_hold.fan_mode.value),
                    set_point_c=widget.hvac_hold.set_point,
                    set_point_auto_heating_c=widget.hvac_hold.set_point_auto[0] if getattr(getattr(widget, 'hvac_hold'), 'set_point_auto') is not None else None,
                    set_point_auto_cooling_c=widget.hvac_hold.set_point_auto[1] if getattr(getattr(widget, 'hvac_hold'), 'set_point_auto') is not None else None,
                    expire_at_estimated=widget.hvac_hold.expire_at_estimated,
                    expire_at_actual=widget.hvac_hold.expire_at_actual,
                    created_at=widget.hvac_hold.created_at,
                    updated_at=widget.hvac_hold.modified_at
                )
                for widget in widgets
                if widget.hvac_hold is not None
            ]


# Temperature dashboard data
@log_returned_data
def get_temperature_dashboards(organization_id: UUID) -> List[TemperatureDashboard]:
    for tx in edgedb_client.transaction():
        with tx:
            temperature_dashboards = tx.query(
                '''
                SELECT TemperatureDashboard {
                    id,
                    name,
                    created_at,
                    modified_at,
                    location: {
                        id
                    }
                }
                FILTER .organization.id = <uuid>$organization_id
                ''',
                organization_id=organization_id
            )
            return [
                TemperatureDashboard(
                    temperature_dashboard_id=temperature_dashboard.id,
                    name=temperature_dashboard.name,
                    location_id=temperature_dashboard.location.id,
                    created_at=temperature_dashboard.created_at,
                    updated_at=temperature_dashboard.modified_at
                )
                for temperature_dashboard in temperature_dashboards
            ]

@log_returned_data
def get_temperature_unit_widgets_for_dashboard(temperature_dashboard_id: UUID) -> List[TemperatureUnitWidget]:
    for tx in edgedb_client.transaction():
        with tx:
            widgets = tx.query(
                '''
                SELECT TemperatureUnit {
                    id,
                    name,
                    lower_temperature_c,
                    upper_temperature_c,
                    alert_window_s,
                    appliance,
                    temperature_place: {
                        id
                    },
                    created_at,
                    modified_at
                }
                FILTER .dashboard.id = <uuid>$temperature_dashboard_id
                ''',
                temperature_dashboard_id=temperature_dashboard_id
            )
            return [
                TemperatureUnitWidget(
                    temperature_unit_widget_id=widget.id,
                    name=widget.name,
                    low_c=widget.lower_temperature_c,
                    high_c=widget.upper_temperature_c,
                    alert_threshold_s=widget.alert_window_s,
                    appliance_type=ApplianceType(widget.appliance.value),
                    temperature_sensor_place_id=widget.temperature_place.id,
                    temperature_dashboard_id=temperature_dashboard_id,
                    created_at=widget.created_at,
                    updated_at=widget.modified_at
                )
                for widget in widgets
            ]


# Electric dashboard data
@log_returned_data
def get_electric_dashboards(organization_id: UUID) -> List[ElectricityDashboard]:
    for tx in edgedb_client.transaction():
        with tx:
            electric_dashboards = tx.query(
                '''
                SELECT ElectricityDashboard {
                    id,
                    name,
                    created_at,
                    modified_at,
                    location: {
                        id
                    }
                }
                FILTER .organization.id = <uuid>$organization_id
                ''',
                organization_id=organization_id
            )
            return [
                ElectricityDashboard(
                    electric_dashboard_id=electric_dashboard.id,
                    name=electric_dashboard.name,
                    location_id=electric_dashboard.location.id,
                    created_at=electric_dashboard.created_at,
                    updated_at=electric_dashboard.modified_at
                )
                for electric_dashboard in electric_dashboards
            ]

@log_returned_data
def get_energy_consumption_breakdown_electric_widgets_for_dashboard(electric_dashboard_id: UUID) -> List[EnergyConsumptionBreakdownElectricWidget]:
    for tx in edgedb_client.transaction():
        with tx:
            widgets = tx.query(
                '''
                SELECT EnergyConsumptionBreakdown {
                    id,
                    name,
                    created_at,
                    modified_at
                }
                FILTER .dashboard.id = <uuid>$electric_dashboard_id
                ''',
                electric_dashboard_id=electric_dashboard_id
            )
            return [
                EnergyConsumptionBreakdownElectricWidget(
                    electric_widget_id=widget.id,
                    name=widget.name,
                    electric_dashboard_id=electric_dashboard_id,
                    created_at=widget.created_at,
                    updated_at=widget.modified_at
                )
                for widget in widgets
            ]

@log_returned_data
def get_energy_load_curve_electric_widgets_for_dashboard(electric_dashboard_id: UUID) -> List[EnergyLoadCurveElectricWidget]:
    for tx in edgedb_client.transaction():
        with tx:
            widgets = tx.query(
                '''
                SELECT EnergyLoadCurve {
                    id,
                    name,
                    created_at,
                    modified_at
                }
                FILTER .dashboard.id = <uuid>$electric_dashboard_id
                ''',
                electric_dashboard_id=electric_dashboard_id
            )
            return [
                EnergyLoadCurveElectricWidget(
                    electric_widget_id=widget.id,
                    name=widget.name,
                    electric_dashboard_id=electric_dashboard_id,
                    created_at=widget.created_at,
                    updated_at=widget.modified_at
                )
                for widget in widgets
            ]

@log_returned_data
def get_panel_system_health_electric_widgets_for_dashboard(electric_dashboard_id: UUID) -> List[PanelSystemHealthElectricWidget]:
    for tx in edgedb_client.transaction():
        with tx:
            widgets = tx.query(
                '''
                SELECT PanelSystemHealth {
                    id,
                    name,
                    created_at,
                    modified_at
                }
                FILTER .dashboard.id = <uuid>$electric_dashboard_id
                ''',
                electric_dashboard_id=electric_dashboard_id
            )
            return [
                PanelSystemHealthElectricWidget(
                    electric_widget_id=widget.id,
                    name=widget.name,
                    electric_dashboard_id=electric_dashboard_id,
                    created_at=widget.created_at,
                    updated_at=widget.modified_at
                )
                for widget in widgets
            ]




def main(
    organization_id: UUID
):
    logger.info(f'Importing data for organization: {organization_id}')

    organization = get_organization(organization_id)
    organization_feature_toggles = get_organization_feature_toggles(organization_id)
    organization_owner_user = get_organization_owner_user(organization_id)
    users = get_users(organization_id)
    organization_users: List[OrganizationUser] = [
        OrganizationUser(
            organization_id=organization.organization_id,
            user_id=user.user_id,
            is_organization_owner=(user.user_id == organization_owner_user.user_id),
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        for user in users
    ]
    
    operating_range_notification_settings = get_operating_range_notification_settings(organization_id)

    user_location_access_grants = get_user_location_access_grants(organization_id)
    user_organization_access_grants = get_user_organization_access_grants(organization_id)


    locations = get_locations(organization_id)

    appliances: List[Appliance] = []
    circuits: List[Circuit] = []
    clamps: List[Clamp] = []
    electric_sensors: List[ElectricSensor] = []
    electric_panels: List[ElectricPanel] = []
    gateways: List[Gateway] = []
    hvac_zones: List[HvacZone] = []
    location_electricity_prices: List[LocationElectricityPrice] = []
    location_operating_hours: List[LocationOperatingHours] = []
    location_time_of_use_rates: List[LocationTimeOfUseRate] = []
    nodes: List[Node] = []
    temperature_ranges: List[TemperatureRange] = []
    temperature_sensor_place_alerts: List[TemperatureSensorPlaceAlert] = []
    temperature_sensor_places: List[TemperatureSensorPlace] = []
    temperature_sensors: List[TemperatureSensor] = []
    thermostats: List[Thermostat] = []
    for location in locations:
        location_hvac_zones = get_hvac_zones(location.location_id)
        appliances.extend(get_appliances(location_id=location.location_id))
        circuits.extend(get_circuits(location_id=location.location_id))
        clamps.extend(get_clamps(location.location_id))
        electric_sensors.extend(get_electric_sensors(location.location_id))
        electric_panels.extend(get_electric_panels(location.location_id))
        gateways.extend(get_gateways(location.location_id))
        hvac_zones.extend(location_hvac_zones)
        location_electricity_prices.extend(get_location_electricity_prices(location.location_id))
        location_operating_hours.extend(get_location_operating_hours(location.location_id))
        location_time_of_use_rates.extend(get_location_time_of_use_rates(location.location_id))
        nodes.extend(get_nodes(location.location_id))
        temperature_ranges.extend(get_temperature_ranges(location.location_id))
        temperature_sensor_place_alerts.extend(get_temperature_sensor_place_alerts(location.location_id))
        temperature_sensor_places.extend(get_temperature_senors_places(location.location_id))
        temperature_sensors.extend(get_temperature_sensors(location.location_id))
    

    electric_dashboards = get_electric_dashboards(organization_id)
    energy_consumption_breakdown_widgets: List[EnergyConsumptionBreakdownElectricWidget] = []
    energy_load_curve_widgets: List[EnergyLoadCurveElectricWidget] = []
    panel_system_health_widgets: List[PanelSystemHealthElectricWidget] = []
    for electric_dashbaord in electric_dashboards:
        energy_consumption_breakdown_widgets.extend(get_energy_consumption_breakdown_electric_widgets_for_dashboard(electric_dashboard_id=electric_dashbaord.electric_dashboard_id))
        energy_load_curve_widgets.extend(get_energy_load_curve_electric_widgets_for_dashboard(electric_dashboard_id=electric_dashbaord.electric_dashboard_id))
        panel_system_health_widgets.extend(get_panel_system_health_electric_widgets_for_dashboard(electric_dashboard_id=electric_dashbaord.electric_dashboard_id))


    hvac_dashboards = get_hvac_dashboards(organization_id)
    control_zone_widgets: List[ControlZoneHvacWidget] = []
    for hvac_dashboard in hvac_dashboards:
        control_zone_widgets.extend(get_control_zone_hvac_widgets_for_dashboard(hvac_dashboard_id=hvac_dashboard.hvac_dashboard_id, hvac_zones=hvac_zones))
    
    for location in locations:
        thermostats.extend(get_thermostats(location.location_id, control_zone_widgets))

    hvac_holds = get_hvac_holds_for_organization(organization_id)
    hvac_schedules = get_hvac_schedules(organization_id)


    temperature_dashboards = get_temperature_dashboards(organization_id)
    temperature_unit_widgets: List[TemperatureUnitWidget] = []
    for temperature_dashboard in temperature_dashboards:
        temperature_unit_widgets.extend(get_temperature_unit_widgets_for_dashboard(temperature_dashboard_id=temperature_dashboard.temperature_dashboard_id))


    if not DRY_RUN:
        logger.info('Committing data to postgres...')
        postgres_session.add(organization)
        postgres_session.add_all(organization_feature_toggles)
        if len(users) > 0:
            postgres_session.execute(
                insert(User)
                .values([{
                    'user_id': user.user_id,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': user.phone_number,
                    'password_hash': user.password_hash,
                    'created_at': user.created_at,
                    'updated_at': user.updated_at
                } for user in users])
                .on_conflict_do_nothing()
            )
        postgres_session.add_all(organization_users)
        postgres_session.add_all(operating_range_notification_settings)
        if len(user_location_access_grants) > 0:
            postgres_session.execute(
                insert(UserLocationAccessGrant)
                .values([{
                    'user_id': str(user_location_access_grant.user_id),
                    'location_id': str(user_location_access_grant.location_id),
                    'location_access_grant': user_location_access_grant.location_access_grant.value,
                    'created_at': user_location_access_grant.created_at,
                } for user_location_access_grant in user_location_access_grants])
                .on_conflict_do_nothing()
            )
        if len(user_organization_access_grants) > 0:
            postgres_session.execute(
                insert(UserOrganizationAccessGrant)
                .values([{
                    'user_id': user_organization_access_grant.user_id,
                    'organization_id': user_organization_access_grant.organization_id,
                    'organization_access_grant': user_organization_access_grant.organization_access_grant.value,
                    'created_at': user_organization_access_grant.created_at,
                } for user_organization_access_grant in user_organization_access_grants])
                .on_conflict_do_nothing()
            )

        postgres_session.add_all(locations)
        postgres_session.add_all(electric_panels)
        postgres_session.add_all(circuits)
        postgres_session.add_all(clamps)
        postgres_session.add_all(electric_sensors)
        postgres_session.add_all(gateways)
        postgres_session.add_all(hvac_zones)
        postgres_session.add_all(location_electricity_prices)
        postgres_session.add_all(location_operating_hours)
        postgres_session.add_all(location_time_of_use_rates)
        postgres_session.add_all(nodes)
        postgres_session.add_all(temperature_ranges)
        postgres_session.add_all(temperature_sensor_place_alerts)
        postgres_session.add_all(temperature_sensor_places)
        postgres_session.add_all(temperature_sensors)
        postgres_session.add_all(thermostats)

        postgres_session.add_all(electric_dashboards)
        postgres_session.add_all(energy_consumption_breakdown_widgets)
        postgres_session.add_all(energy_load_curve_widgets)
        postgres_session.add_all(panel_system_health_widgets)

        postgres_session.add_all(hvac_dashboards)
        postgres_session.add_all(control_zone_widgets)

        postgres_session.add_all(hvac_holds)
        postgres_session.add_all(hvac_schedules)

        postgres_session.add_all(temperature_dashboards)
        postgres_session.add_all(temperature_unit_widgets)
        
        postgres_session.commit()
        logger.info('Committing data to postgres...Done')
    else:
        logger.info('Dry run mode enabled. Skipping commit to postgres.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Import organization data from edgedb'
    )
    parser.add_argument(
        'organization_id',
        type=str,
        help='Organization ID'
    )
    args = parser.parse_args()
    arg_organization_id = args.organization_id
    
    main(organization_id=UUID(arg_organization_id))
