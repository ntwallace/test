import argparse
import logging
import os
from typing import List
from uuid import UUID

from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.v1.auth.models.user_location_access_grant import UserLocationAccessGrant
from app.v1.auth.models.user_organization_access_grant import UserOrganizationAccessGrant
from app.v1.electricity_dashboards.models.electricity_dashboard import ElectricityDashboard
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
from app.v1.organizations.models.organization_feature_toggle import OrganizationFeatureToggle
from app.v1.organizations.models.organization import Organization
from app.v1.organizations.models.organization_user import OrganizationUser
from app.v1.temperature_dashboards.models.temperature_dashboard import TemperatureDashboard
from app.v1.temperature_monitoring.models.temperature_range import TemperatureRange
from app.v1.temperature_monitoring.models.temperature_sensor import TemperatureSensor
from app.v1.temperature_monitoring.models.temperature_sensor_place import TemperatureSensorPlace
from app.v1.temperature_monitoring.models.temperature_sensor_place_alert import TemperatureSensorPlaceAlert
from app.v1.users.models.user import User
from app.v1.electricity_dashboards.models.energy_consumption_breakdown_electric_widget import EnergyConsumptionBreakdownElectricWidget
from app.v1.electricity_dashboards.models.energy_load_curve_electric_widget import EnergyLoadCurveElectricWidget
from app.v1.electricity_dashboards.models.panel_system_health_electric_widget import PanelSystemHealthElectricWidget
from app.v1.hvac_dashboards.models.hvac_dashboard import HvacDashboard
from app.v1.hvac.models.hvac_hold import HvacHold
from app.v1.hvac.models.hvac_schedule import HvacSchedule, HvacScheduleEvent
from app.v1.hvac_dashboards.models.control_zone_hvac_widget import ControlZoneHvacWidget
from app.v3_adapter.operating_range_notification_settings.models import OperatingRangeNotificationSettings
from app.v1.temperature_dashboards.models.temeprature_unit_widget import TemperatureUnitWidget

load_dotenv()

TEST_POSTGRES_CONNECTION = True
DRY_RUN = os.environ['DRY_RUN'].lower() == 'true' if os.environ.get('DRY_RUN', None) is not None else True

POWERX_DATABASE_HOST = os.environ['MIGRATION_POWERX_DATABASE_HOST']
POWERX_DATABASE_PORT = os.environ['MIGRATION_POWERX_DATABASE_PORT']
POWERX_DATABASE_USER = os.environ['MIGRATION_POWERX_DATABASE_USER']
POWERX_DATABASE_PASSWORD = os.environ['MIGRATION_POWERX_DATABASE_PASSWORD']
POWERX_DATABASE_NAME = os.environ['MIGRATION_POWERX_DATABASE_NAME']
POWERX_DATABASE_URL = f"postgresql://{POWERX_DATABASE_USER}:{POWERX_DATABASE_PASSWORD}@{POWERX_DATABASE_HOST}:{POWERX_DATABASE_PORT}/{POWERX_DATABASE_NAME}"


logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

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
        logger.info('')
        logger.info(f'{func.__name__}:')
        result = func(*args, **kwargs)
        logger.info(result)
        return result

    return wrapper

@log_returned_data
def get_oragnization(organization_id: UUID) -> Organization:
    organization = postgres_session.query(Organization).filter_by(organization_id=organization_id).first()
    if organization is None:
        raise Exception(f'Organization with ID {organization_id} not found')
    return organization

@log_returned_data
def get_organization_feature_toggles(organization_id: UUID) -> List[OrganizationFeatureToggle]:
    return postgres_session.query(
        OrganizationFeatureToggle
    ).filter_by(
        organization_id=organization_id
    ).all()

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
def get_organization_users(organization_id: UUID) -> List[OrganizationUser]:
    return postgres_session.query(
        OrganizationUser
    ).filter_by(
        organization_id=organization_id
    ).all()

@log_returned_data
def get_oganization_operating_range_notification_settings(organization_id: UUID) -> List[OperatingRangeNotificationSettings]:
    return postgres_session.query(
        OperatingRangeNotificationSettings
    ).join(
        Location, Location.location_id==OperatingRangeNotificationSettings.location_id
    ).filter(
        Location.organization_id==organization_id
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
def get_user_organization_access_grants(organization_id: UUID) -> List[UserOrganizationAccessGrant]:
    return postgres_session.query(
        UserOrganizationAccessGrant
    ).filter_by(
        organization_id=organization_id
    ).all()

@log_returned_data
def get_locations(organization_id: UUID) -> List[Location]:
    return postgres_session.query(
        Location
    ).filter_by(
        organization_id=organization_id
    ).all()

@log_returned_data
def get_electric_panels(organization_id: UUID) -> List[ElectricPanel]:
    return postgres_session.query(
        ElectricPanel
    ).join(
        Location, Location.location_id==ElectricPanel.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_circuits(organization_id: UUID) -> List[Circuit]:
    return postgres_session.query(
        Circuit
    ).join(
        ElectricPanel, ElectricPanel.electric_panel_id==Circuit.electric_panel_id
    ).join(
        Location, Location.location_id==ElectricPanel.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_clamps(organization_id: UUID) -> List[Clamp]:
    return postgres_session.query(
        Clamp
    ).join(
        ElectricSensor, ElectricSensor.electric_sensor_id==Clamp.electric_sensor_id
    ).join(
        ElectricPanel, ElectricPanel.electric_panel_id==ElectricSensor.electric_panel_id
    ).join(
        Location, Location.location_id==ElectricPanel.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_electric_sensors(organization_id: UUID) -> List[ElectricSensor]:
    return postgres_session.query(
        ElectricSensor
    ).join(
        ElectricPanel, ElectricPanel.electric_panel_id==ElectricSensor.electric_panel_id
    ).join(
        Location, Location.location_id==ElectricPanel.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_gateways(organization_id: UUID) -> List[Gateway]:
    return postgres_session.query(
        Gateway
    ).join(
        Location, Location.location_id==Gateway.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_hvac_zones(organization_id: UUID) -> List[HvacZone]:
    return postgres_session.query(
        HvacZone
    ).join(
        Location, Location.location_id==HvacZone.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_location_electricity_prices(organization_id: UUID) -> List[LocationElectricityPrice]:
    return postgres_session.query(
        LocationElectricityPrice
    ).join(
        Location, Location.location_id==LocationElectricityPrice.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_location_operating_hours(organization_id: UUID) -> List[LocationOperatingHours]:
    return postgres_session.query(
        LocationOperatingHours
    ).join(
        Location, Location.location_id==LocationOperatingHours.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_location_time_of_use_rates(organization_id: UUID) -> List[LocationTimeOfUseRate]:
    return postgres_session.query(
        LocationTimeOfUseRate
    ).join(
        Location, Location.location_id==LocationTimeOfUseRate.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_nodes(organization_id: UUID) -> List[Node]:
    return postgres_session.query(
        Node
    ).join(
        Gateway, Gateway.gateway_id==Node.gateway_id
    ).join(
        Location, Location.location_id==Gateway.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_temperature_ranges(organization_id: UUID) -> List[TemperatureRange]:
    return postgres_session.query(
        TemperatureRange
    ).join(
        TemperatureSensorPlace, TemperatureSensorPlace.temperature_sensor_place_id==TemperatureRange.temperature_sensor_place_id
    ).join(
        Location, Location.location_id==TemperatureSensorPlace.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_temperature_sensor_place_alerts(organization_id: UUID) -> List[TemperatureSensorPlaceAlert]:
    return postgres_session.query(
        TemperatureSensorPlaceAlert
    ).join(
        TemperatureSensorPlace, TemperatureSensorPlace.temperature_sensor_place_id==TemperatureSensorPlaceAlert.temperature_sensor_place_id
    ).join(
        Location, Location.location_id==TemperatureSensorPlace.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_temperature_sensor_places(organization_id: UUID) -> List[TemperatureSensorPlace]:
    return postgres_session.query(
        TemperatureSensorPlace
    ).join(
        Location, Location.location_id==TemperatureSensorPlace.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_temperature_sensors(organization_id: UUID) -> List[TemperatureSensor]:
    return postgres_session.query(
        TemperatureSensor
    ).join(
        Location, Location.location_id==TemperatureSensor.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_thermostats(organization_id: UUID) -> List[Thermostat]:
    return postgres_session.query(
        Thermostat
    ).join(
        HvacZone, HvacZone.hvac_zone_id==Thermostat.hvac_zone_id
    ).join(
        Location, Location.location_id==HvacZone.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_electric_dashboards(organization_id: UUID) -> List[ElectricityDashboard]:
    return postgres_session.query(
        ElectricityDashboard
    ).join(
        Location, Location.location_id==ElectricityDashboard.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_energy_consumption_breakdown_widgets(organization_id: UUID) -> List[EnergyConsumptionBreakdownElectricWidget]:
    return postgres_session.query(
        EnergyConsumptionBreakdownElectricWidget
    ).join(
        ElectricityDashboard, ElectricityDashboard.electricity_dashboard_id==EnergyConsumptionBreakdownElectricWidget.electric_dashboard_id
    ).join(
        Location, Location.location_id==ElectricityDashboard.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_energy_load_curve_widgets(organization_id: UUID) -> List[EnergyLoadCurveElectricWidget]:
    return postgres_session.query(
        EnergyLoadCurveElectricWidget
    ).join(
        ElectricityDashboard, ElectricityDashboard.electricity_dashboard_id==EnergyLoadCurveElectricWidget.electric_dashboard_id
    ).join(
        Location, Location.location_id==ElectricityDashboard.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_panel_system_health_widgets(organization_id: UUID) -> List[PanelSystemHealthElectricWidget]:
    return postgres_session.query(
        PanelSystemHealthElectricWidget
    ).join(
        ElectricityDashboard, ElectricityDashboard.electricity_dashboard_id==PanelSystemHealthElectricWidget.electric_dashboard_id
    ).join(
        Location, Location.location_id==ElectricityDashboard.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_hvac_dashboards(organization_id: UUID) -> List[HvacDashboard]:
    return postgres_session.query(
        HvacDashboard
    ).join(
        Location, Location.location_id==HvacDashboard.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_control_zone_widgets(organization_id: UUID) -> List[ControlZoneHvacWidget]:
    return postgres_session.query(
        ControlZoneHvacWidget
    ).join(
        HvacDashboard, HvacDashboard.hvac_dashboard_id==ControlZoneHvacWidget.hvac_dashboard_id
    ).join(
        Location, Location.location_id==HvacDashboard.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_hvac_holds(organization_id: UUID) -> List[HvacHold]:
    return postgres_session.query(
        HvacHold
    ).join(
        ControlZoneHvacWidget, ControlZoneHvacWidget.hvac_widget_id==HvacHold.control_zone_hvac_widget_id
    ).join(
        HvacDashboard, HvacDashboard.hvac_dashboard_id==ControlZoneHvacWidget.hvac_dashboard_id
    ).join(
        Location, Location.location_id==HvacDashboard.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_hvac_schedule_events(organization_id: UUID) -> List[HvacScheduleEvent]:
    return postgres_session.query(
        HvacScheduleEvent
    ).join(
        HvacSchedule, HvacSchedule.hvac_schedule_id==HvacScheduleEvent.hvac_schedule_id
    ).join(
        Location, Location.location_id==HvacSchedule.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_hvac_schedules(organization_id: UUID) -> List[HvacSchedule]:
    return postgres_session.query(
        HvacSchedule
    ).join(
        Location, Location.location_id==HvacSchedule.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_temperature_dashboards(organization_id: UUID) -> List[TemperatureDashboard]:
    return postgres_session.query(
        TemperatureDashboard
    ).join(
        Location, Location.location_id==TemperatureDashboard.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()

@log_returned_data
def get_temperature_unit_widgets(organization_id: UUID) -> List[TemperatureUnitWidget]:
    return postgres_session.query(
        TemperatureUnitWidget
    ).join(
        TemperatureDashboard, TemperatureDashboard.temperature_dashboard_id==TemperatureUnitWidget.temperature_dashboard_id
    ).join(
        Location, Location.location_id==TemperatureDashboard.location_id
    ).filter(
        Location.organization_id==organization_id
    ).all()


def main(organization_id: UUID):
    organization = get_oragnization(organization_id)
    organization_feature_toggles = get_organization_feature_toggles(organization.organization_id)
    organization_users = get_organization_users(organization.organization_id)
    operating_range_notification_settings = get_oganization_operating_range_notification_settings(organization.organization_id)
    user_location_access_grants = get_user_location_access_grants(organization.organization_id)
    user_organization_access_grants = get_user_organization_access_grants(organization.organization_id)
    
    locations = get_locations(organization.organization_id)
    electric_panels = get_electric_panels(organization.organization_id)
    circuits = get_circuits(organization.organization_id)
    clamps = get_clamps(organization.organization_id)
    electric_sensors = get_electric_sensors(organization.organization_id)
    gateways = get_gateways(organization.organization_id)
    hvac_zones = get_hvac_zones(organization.organization_id)
    location_electricity_prices = get_location_electricity_prices(organization.organization_id)
    location_operating_hours = get_location_operating_hours(organization.organization_id)
    location_time_of_use_rates = get_location_time_of_use_rates(organization.organization_id)
    nodes = get_nodes(organization.organization_id)
    temperature_ranges = get_temperature_ranges(organization.organization_id)
    temperature_sensor_place_alerts = get_temperature_sensor_place_alerts(organization.organization_id)
    temperature_sensor_places = get_temperature_sensor_places(organization.organization_id)
    temperature_sensors = get_temperature_sensors(organization.organization_id)
    thermostats = get_thermostats(organization.organization_id)
    
    electric_dashboards = get_electric_dashboards(organization.organization_id)
    energy_consumption_breakdown_widgets = get_energy_consumption_breakdown_widgets(organization.organization_id)
    energy_load_curve_widgets = get_energy_load_curve_widgets(organization.organization_id)
    panel_system_health_widgets = get_panel_system_health_widgets(organization.organization_id)

    hvac_dashboards = get_hvac_dashboards(organization.organization_id)
    control_zone_widgets = get_control_zone_widgets(organization.organization_id)

    hvac_holds = get_hvac_holds(organization.organization_id)
    hvac_schedule_events = get_hvac_schedule_events(organization.organization_id)
    hvac_schedules = get_hvac_schedules(organization.organization_id)

    temperature_dashboards = get_temperature_dashboards(organization.organization_id)
    temperature_unit_widgets = get_temperature_unit_widgets(organization.organization_id)

    # Delete all data for the organization in reverse order
    if not DRY_RUN:
        logger.info(f'Deleting data for organization {organization.organization_id}')

        logger.info('Deleting temperature unit widgets')
        for temperature_unit_widget in temperature_unit_widgets:
            postgres_session.delete(temperature_unit_widget)
        logger.info('Deleting temperature dashboards')
        for temperature_dashboard in temperature_dashboards:
            postgres_session.delete(temperature_dashboard)
        for hvac_schedule_event in hvac_schedule_events:
            postgres_session.delete(hvac_schedule_event)
        logger.info('Deleting hvac schedules')
        for hvac_schedule in hvac_schedules:
            postgres_session.delete(hvac_schedule)
        logger.info('Deleting hvac holds')
        for hvac_hold in hvac_holds:
            postgres_session.delete(hvac_hold)
        logger.info('Deleting control zone widgets')
        for control_zone_widget in control_zone_widgets:
            postgres_session.delete(control_zone_widget)
        logger.info('Deleting hvac dashboards')
        for dashboard in hvac_dashboards:
            postgres_session.delete(dashboard)
        logger.info('Deleting panel system health widgets')
        for widget in panel_system_health_widgets:
            postgres_session.delete(widget)
        logger.info('Deleting energy load curve widgets')
        for widget in energy_load_curve_widgets:
            postgres_session.delete(widget)
        logger.info('Deleting energy consumption breakdown widgets')
        for widget in energy_consumption_breakdown_widgets:
            postgres_session.delete(widget)
        logger.info('Deleting electric dashboards')
        for dashboard in electric_dashboards:
            postgres_session.delete(dashboard)
        logger.info('Deleting thermostats')
        for thermostat in thermostats:
            postgres_session.delete(thermostat)
        logger.info('Deleting temperature sensors')
        for sensor in temperature_sensors:
            postgres_session.delete(sensor)
        logger.info('Deleting temperature sensor places')
        for sensor_place in temperature_sensor_places:
            postgres_session.delete(sensor_place)
        logger.info('Deleting temperature sensor place alerts')
        for sensor_alert in temperature_sensor_place_alerts:
            postgres_session.delete(sensor_alert)
        logger.info('Deleting temperature ranges')
        for temperature_range in temperature_ranges:
            postgres_session.delete(temperature_range)
        logger.info('Deleting nodes')
        for node in nodes:
            postgres_session.delete(node)
        logger.info('Deleting location time of use rates')
        for rate in location_time_of_use_rates:
            postgres_session.delete(rate)
        logger.info('Deleting location operating hours')
        for hours in location_operating_hours:
            postgres_session.delete(hours)
        logger.info('Deleting location electricity prices')
        for price in location_electricity_prices:
            postgres_session.delete(price)
        logger.info('Deleting hvac zones')
        for zone in hvac_zones:
            postgres_session.delete(zone)
        logger.info('Deleting gateways')
        for gateway in gateways:
            postgres_session.delete(gateway)
        logger.info('Deleting electric sensors')
        for sensor in electric_sensors:
            postgres_session.delete(sensor)
        logger.info('Deleting clamps')
        for clamp in clamps:
            postgres_session.delete(clamp)
        logger.info('Deleting circuits')
        for circuit in circuits:
            postgres_session.delete(circuit)
        logger.info('Deleting electric panels')
        for panel in electric_panels:
            postgres_session.delete(panel)
        logger.info('Deleting locations')
        for location in locations:
            postgres_session.delete(location)
        logger.info('Deleting user organization access grants')
        for grant in user_organization_access_grants:
            postgres_session.delete(grant)
        logger.info('Deleting user location access grants')
        for grant in user_location_access_grants:
            postgres_session.delete(grant)
        logger.info('Deleting organization operating range notification settings')
        for setting in operating_range_notification_settings:
            postgres_session.delete(setting)
        logger.info('Deleting organization users')
        for organization_user in organization_users:
            postgres_session.delete(organization_user)
        logger.info('Deleting organization feature toggles')
        for toggle in organization_feature_toggles:
            postgres_session.delete(toggle)
        logger.info('Deleting organization')
        postgres_session.delete(organization)
        
        postgres_session.commit()
        logger.info('Deleting organization data...Done')
    else:
        logger.info('Dry run completed. No data was deleted.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Delete organization data from Postgres'
    )
    parser.add_argument(
        'organization_id',
        type=str,
        help='Organization ID'
    )
    args = parser.parse_args()
    arg_organization_id = UUID(args.organization_id)
    main(organization_id=arg_organization_id)
