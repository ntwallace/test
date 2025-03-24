import argparse
from datetime import datetime, time
import json
import logging
import os
from typing import List
from uuid import UUID

from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.v1.auth.models.user_location_access_grant import UserLocationAccessGrant
from app.v1.electricity_dashboards.models.electricity_dashboard import ElectricityDashboard
from app.v1.electricity_dashboards.models.energy_consumption_breakdown_electric_widget import EnergyConsumptionBreakdownElectricWidget
from app.v1.electricity_dashboards.models.energy_load_curve_electric_widget import EnergyLoadCurveElectricWidget
from app.v1.electricity_dashboards.models.panel_system_health_electric_widget import PanelSystemHealthElectricWidget
from app.v1.electricity_monitoring.models.circuit import Circuit
from app.v1.electricity_monitoring.models.clamp import Clamp
from app.v1.electricity_monitoring.models.electric_panel import ElectricPanel
from app.v1.electricity_monitoring.models.electric_sensor import ElectricSensor
from app.v1.hvac.models.hvac_zone import HvacZone
from app.v1.hvac.models.thermostat import Thermostat
from app.v1.locations.models.location import Location
from app.v1.locations.models.location_electricity_price import LocationElectricityPrice
from app.v1.locations.models.location_operating_hours import LocationOperatingHours
from app.v1.locations.models.location_time_of_use_rate import LocationTimeOfUseRate
from app.v1.mesh_network.models.gateway import Gateway
from app.v1.mesh_network.models.node import Node
from app.v1.organizations.models.organization import Organization
from app.v1.organizations.models.organization_user import OrganizationUser
from app.v1.temperature_dashboards.models.temperature_dashboard import TemperatureDashboard
from app.v1.temperature_monitoring.models.temperature_range import TemperatureRange
from app.v1.temperature_monitoring.models.temperature_sensor import TemperatureSensor
from app.v1.temperature_monitoring.models.temperature_sensor_place import TemperatureSensorPlace
from app.v1.temperature_monitoring.models.temperature_sensor_place_alert import TemperatureSensorPlaceAlert
from app.v1.users.models.user import User
from app.v1.hvac_dashboards.models.hvac_dashboard import HvacDashboard
from app.v1.hvac.models.hvac_hold import HvacHold
from app.v1.hvac.models.hvac_schedule import HvacSchedule, HvacScheduleEvent
from app.v1.hvac_dashboards.models.control_zone_hvac_widget import ControlZoneHvacWidget
from app.v1.temperature_dashboards.models.temeprature_unit_widget import TemperatureUnitWidget


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

load_dotenv()

TEST_POSTGRES_CONNECTION = True
DRY_RUN = os.environ['DRY_RUN'].lower() == 'true' if os.environ.get('DRY_RUN', None) is not None else True

POWERX_DATABASE_HOST = os.environ['POWERX_DATABASE_HOST']
POWERX_DATABASE_PORT = os.environ['POWERX_DATABASE_PORT']
POWERX_DATABASE_USER = os.environ['POWERX_DATABASE_USER']
POWERX_DATABASE_PASSWORD = os.environ['POWERX_DATABASE_PASSWORD']
POWERX_DATABASE_NAME = os.environ['POWERX_DATABASE_NAME']
POWERX_DATABASE_URL = f"postgresql://{POWERX_DATABASE_USER}:{POWERX_DATABASE_PASSWORD}@{POWERX_DATABASE_HOST}:{POWERX_DATABASE_PORT}/{POWERX_DATABASE_NAME}"

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
    postgres_session.execute(text('SELECT 1'))


def log_returned_data(func):
    def wrapper(*args, **kwargs):
        # logger.info('')
        # logger.info(f'{func.__name__}:')
        result = func(*args, **kwargs)
        # logger.info(result)
        return result

    return wrapper

@log_returned_data
def get_organization(location_id: UUID) -> Organization:
    organization = postgres_session.query(
        Organization
    ).join(
        Location, Location.organization_id==Organization.organization_id
    ).filter(
        Location.location_id==location_id
    ).first()
    if organization is None:
        raise ValueError(f"Organization for location with ID {location_id} not found")
    return organization

@log_returned_data
def get_users(organization_id: UUID) -> List[User]:
    return postgres_session.query(
        User
    ).join(
        OrganizationUser, User.user_id==OrganizationUser.user_id
    ).filter(
        OrganizationUser.organization_id==organization_id
    ).all()

@log_returned_data
def get_user_location_access_grants(organization_id: UUID) -> List[UserLocationAccessGrant]:
    return postgres_session.query(
        UserLocationAccessGrant
    ).join(
        Location, UserLocationAccessGrant.location_id == Location.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_location(location_id: UUID) -> Location:
    location = postgres_session.query(
        Location
    ).get(
        location_id
    )
    if location is None:
        raise ValueError(f"Location with ID {location_id} not found")
    return location

@log_returned_data
def get_electric_panels(location_id: UUID) -> List[ElectricPanel]:
    return postgres_session.query(
        ElectricPanel
    ).filter(
       ElectricPanel.location_id==location_id
    ).all()

@log_returned_data
def get_circuits(location_id: UUID) -> List[Circuit]:
    return postgres_session.query(
        Circuit
    ).join(
        ElectricPanel, ElectricPanel.electric_panel_id==Circuit.electric_panel_id
    ).filter(
        ElectricPanel.location_id==location_id
    ).all()

@log_returned_data
def get_clamps(location_id: UUID) -> List[Clamp]:
    return postgres_session.query(
        Clamp
    ).join(
        ElectricSensor, ElectricSensor.electric_sensor_id==Clamp.electric_sensor_id
    ).join(
        ElectricPanel, ElectricPanel.electric_panel_id==ElectricSensor.electric_panel_id
    ).filter(
        ElectricPanel.location_id==location_id
    ).all()

@log_returned_data
def get_electric_sensors(location_id: UUID) -> List[ElectricSensor]:
    return postgres_session.query(
        ElectricSensor
    ).join(
        ElectricPanel, ElectricPanel.electric_panel_id==ElectricSensor.electric_panel_id
    ).filter(
        ElectricPanel.location_id==location_id
    ).all()

@log_returned_data
def get_gateways(location_id: UUID) -> List[Gateway]:
    return postgres_session.query(
        Gateway
    ).filter(
        Gateway.location_id==location_id
    ).all()

@log_returned_data
def get_hvac_zones(location_id: UUID) -> List[HvacZone]:
    return postgres_session.query(
        HvacZone
    ).filter(
        HvacZone.location_id==location_id
    ).all()

@log_returned_data
def get_location_electricity_prices(location_id: UUID) -> List[LocationElectricityPrice]:
    return postgres_session.query(
        LocationElectricityPrice
    ).filter(
        LocationElectricityPrice.location_id==location_id
    ).all()

@log_returned_data
def get_location_operating_hours(location_id: UUID) -> List[LocationOperatingHours]:
    return postgres_session.query(
        LocationOperatingHours
    ).filter(
        LocationOperatingHours.location_id==location_id
    ).all()

@log_returned_data
def get_location_time_of_use_rates(location_id: UUID) -> List[LocationTimeOfUseRate]:
    return postgres_session.query(
        LocationTimeOfUseRate
    ).filter(
        LocationTimeOfUseRate.location_id==location_id
    ).all()

@log_returned_data
def get_nodes(location_id: UUID) -> List[Node]:
    return postgres_session.query(
        Node
    ).join(
        Gateway, Gateway.gateway_id==Node.gateway_id
    ).filter(
        Gateway.location_id==location_id
    ).all()

@log_returned_data
def get_temperature_ranges(location_id: UUID) -> List[TemperatureRange]:
    return postgres_session.query(
        TemperatureRange
    ).join(
        TemperatureSensorPlace, TemperatureSensorPlace.temperature_sensor_place_id==TemperatureRange.temperature_sensor_place_id
    ).filter(
        TemperatureSensorPlace.location_id==location_id
    ).all()

@log_returned_data
def get_temperature_sensor_place_alerts(location_id: UUID) -> List[TemperatureSensorPlaceAlert]:
    return postgres_session.query(
        TemperatureSensorPlaceAlert
    ).join(
        TemperatureSensorPlace, TemperatureSensorPlace.temperature_sensor_place_id==TemperatureSensorPlaceAlert.temperature_sensor_place_id
    ).filter(
        TemperatureSensorPlace.location_id==location_id
    ).all()

@log_returned_data
def get_temperature_sensor_places(location_id: UUID) -> List[TemperatureSensorPlace]:
    return postgres_session.query(
        TemperatureSensorPlace
    ).filter(
        TemperatureSensorPlace.location_id==location_id
    ).all()

@log_returned_data
def get_temperature_sensors(location_id: UUID) -> List[TemperatureSensor]:
    return postgres_session.query(
        TemperatureSensor
    ).filter(
        TemperatureSensor.location_id==location_id
    ).all()

@log_returned_data
def get_thermostats(location_id: UUID) -> List[Thermostat]:
    return postgres_session.query(
        Thermostat
    ).join(
        HvacZone, HvacZone.hvac_zone_id==Thermostat.hvac_zone_id
    ).filter(
        HvacZone.location_id==location_id
    ).all()

@log_returned_data
def get_electric_dashboards(location_id: UUID) -> List[ElectricityDashboard]:
    return postgres_session.query(
        ElectricityDashboard
    ).filter(
        ElectricityDashboard.location_id==location_id
    ).all()

@log_returned_data
def get_energy_consumption_breakdown_widgets(location_id: UUID) -> List[EnergyConsumptionBreakdownElectricWidget]:
    return postgres_session.query(
        EnergyConsumptionBreakdownElectricWidget
    ).join(
        ElectricityDashboard, ElectricityDashboard.electricity_dashboard_id==EnergyConsumptionBreakdownElectricWidget.electric_dashboard_id
    ).filter(
        ElectricityDashboard.location_id==location_id
    ).all()

@log_returned_data
def get_energy_load_curve_widgets(location_id: UUID) -> List[EnergyLoadCurveElectricWidget]:
    return postgres_session.query(
        EnergyLoadCurveElectricWidget
    ).join(
        ElectricityDashboard, ElectricityDashboard.electricity_dashboard_id==EnergyLoadCurveElectricWidget.electric_dashboard_id
    ).filter(
        ElectricityDashboard.location_id==location_id
    ).all()

@log_returned_data
def get_panel_system_health_widgets(location_id: UUID) -> List[PanelSystemHealthElectricWidget]:
    return postgres_session.query(
        PanelSystemHealthElectricWidget
    ).join(
        ElectricityDashboard, ElectricityDashboard.electricity_dashboard_id==PanelSystemHealthElectricWidget.electric_dashboard_id
    ).filter(
        ElectricityDashboard.location_id==location_id
    ).all()

@log_returned_data
def get_hvac_dashboards(location_id: UUID) -> List[HvacDashboard]:
    return postgres_session.query(
        HvacDashboard
    ).filter(
        HvacDashboard.location_id==location_id
    ).all()

@log_returned_data
def get_control_zone_widgets(location_id: UUID) -> List[ControlZoneHvacWidget]:
    return postgres_session.query(
        ControlZoneHvacWidget
    ).join(
        HvacDashboard, HvacDashboard.hvac_dashboard_id==ControlZoneHvacWidget.hvac_dashboard_id
    ).filter(
        HvacDashboard.location_id==location_id
    ).all()

@log_returned_data
def get_hvac_holds(location_id: UUID) -> List[HvacHold]:
    return postgres_session.query(
        HvacHold
    ).join(
        ControlZoneHvacWidget, ControlZoneHvacWidget.hvac_widget_id==HvacHold.control_zone_hvac_widget_id
    ).join(
        HvacDashboard, HvacDashboard.hvac_dashboard_id==ControlZoneHvacWidget.hvac_dashboard_id
    ).filter(
        HvacDashboard.location_id==location_id
    ).all()

@log_returned_data
def get_hvac_schedule_events(location_id: UUID) -> List[HvacScheduleEvent]:
    return postgres_session.query(
        HvacScheduleEvent
    ).join(
        HvacSchedule, HvacSchedule.hvac_schedule_id==HvacScheduleEvent.hvac_schedule_id
    ).filter(
        HvacSchedule.location_id==location_id
    ).all()

@log_returned_data
def get_hvac_schedules(location_id: UUID) -> List[HvacSchedule]:
    return postgres_session.query(
        HvacSchedule
    ).filter(
        HvacSchedule.location_id==location_id
    ).all()

@log_returned_data
def get_temperature_dashboards(location_id: UUID) -> List[TemperatureDashboard]:
    return postgres_session.query(
        TemperatureDashboard
    ).filter(
        TemperatureDashboard.location_id==location_id
    ).all()

@log_returned_data
def get_temperature_unit_widgets(location_id: UUID) -> List[TemperatureUnitWidget]:
    return postgres_session.query(
        TemperatureUnitWidget
    ).join(
        TemperatureDashboard, TemperatureDashboard.temperature_dashboard_id==TemperatureUnitWidget.temperature_dashboard_id
    ).filter(
        TemperatureDashboard.location_id==location_id
    ).all()


def main(location_id: UUID):
    organization = get_organization(location_id)

    location = get_location(location_id)

    # user_location_access_grants = get_user_location_access_grants(location_id)

    electric_panels = get_electric_panels(location_id)
    circuits = get_circuits(location_id)
    clamps = get_clamps(location_id)
    electric_sensors = get_electric_sensors(location_id)
    gateways = get_gateways(location_id)
    hvac_zones = get_hvac_zones(location_id)
    location_electricity_prices = get_location_electricity_prices(location_id)
    location_operating_hours = get_location_operating_hours(location_id)
    location_time_of_use_rates = get_location_time_of_use_rates(location_id)
    nodes = get_nodes(location_id)
    temperature_ranges = get_temperature_ranges(location_id)
    temperature_sensor_place_alerts = get_temperature_sensor_place_alerts(location_id)
    temperature_sensor_places = get_temperature_sensor_places(location_id)
    temperature_sensors = get_temperature_sensors(location_id)
    thermostats = get_thermostats(location_id)

    electric_dashboards = get_electric_dashboards(location_id)
    energy_consumption_breakdown_widgets = get_energy_consumption_breakdown_widgets(location_id)
    energy_load_curve_widgets = get_energy_load_curve_widgets(location_id)
    panel_system_health_widgets = get_panel_system_health_widgets(location_id)

    hvac_dashboards = get_hvac_dashboards(location_id)
    control_zone_widgets = get_control_zone_widgets(location_id)

    hvac_holds = get_hvac_holds(location_id)
    hvac_schedule_events = get_hvac_schedule_events(location_id)
    hvac_schedules = get_hvac_schedules(location_id)

    temperature_dashboards = get_temperature_dashboards(location_id)
    temperature_unit_widgets = get_temperature_unit_widgets(location_id)

    filename_to_objects = {
        'organizations': [organization],
        'locations': [location],
        'electric_panels': electric_panels,
        'circuits': circuits,
        'clamps': clamps,
        'electric_sensors': electric_sensors,
        'gateways': gateways,
        'hvac_zones': hvac_zones,
        'location_electricity_prices': location_electricity_prices,
        'location_operating_hours': location_operating_hours,
        'location_time_of_use_rates': location_time_of_use_rates,
        'nodes': nodes,
        'temperature_ranges': temperature_ranges,
        'temperature_sensor_place_alerts': temperature_sensor_place_alerts,
        'temperature_sensor_places': temperature_sensor_places,
        'temperature_sensors': temperature_sensors,
        'thermostats': thermostats,
        'electric_dashboards': electric_dashboards,
        'energy_consumption_breakdown_widgets': energy_consumption_breakdown_widgets,
        'energy_load_curve_widgets': energy_load_curve_widgets,
        'panel_system_health_widgets': panel_system_health_widgets,
        'hvac_dashboards': hvac_dashboards,
        'control_zone_widgets': control_zone_widgets,
        'hvac_holds': hvac_holds,
        'hvac_schedule_events': hvac_schedule_events,
        'hvac_schedules': hvac_schedules,
        'temperature_dashboards': temperature_dashboards,
        'temperature_unit_widgets': temperature_unit_widgets
    }

    base_dir = f'.tmp/{location_id}'
    os.makedirs(base_dir, exist_ok=True)

    for filename, objects in filename_to_objects.items():
        if not DRY_RUN:
            serialize_to_json_file(os.path.join(base_dir, f'{filename}.json'), objects)


def serialize_to_json_file(file_path: str, objects: List):
    serialized_data = [serialize_model(model) for model in objects if model is not None]
    logger.info(f'serialized_data: {serialized_data}')
    with open(file_path, "w") as json_file:
        json.dump(serialized_data, json_file, indent=2)
    logger.info(f"Serialized data written to {file_path}")


def serialize_model(instance):
    """
    Serialize a single SQLAlchemy model instance into a dictionary.
    Handles UUIDs, lists, datetime, and time objects.
    """
    # Use class_mapper to retrieve column attributes
    serialized_data = {}
    for column in instance.__class__.__table__.columns:
        value = getattr(instance, column.name)
        serialized_data[column.name] = serialize_value(value)
    return serialized_data


def serialize_value(value):
    """
    Serialize individual values, handling UUIDs, datetime, time, lists, and more.
    """
    if isinstance(value, UUID):
        return str(value)  # Convert UUID to string
    elif isinstance(value, datetime):
        return value.isoformat()  # Convert datetime to ISO 8601 format
    elif isinstance(value, time):
        return value.isoformat()  # Convert time to ISO 8601 format
    elif isinstance(value, list):
        return [serialize_value(v) for v in value]  # Serialize list elements
    else:
        return value  # Fallback: return value as is (e.g., int, float, str)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Unload location data to a file."
    )
    parser.add_argument(
        'location_id',
        type=str,
        help='Location ID'
    )
    args = parser.parse_args()
    arg_location_id = UUID(args.location_id)
    main(location_id=arg_location_id)
