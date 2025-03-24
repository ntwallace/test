from datetime import datetime, timedelta
from typing import List, Optional
from unittest.mock import Mock
from uuid import uuid4

import pytest

from sqlalchemy.orm import Session

from app.v1.appliances.schemas.appliance import Appliance
from app.v1.appliances.schemas.appliance_type import ApplianceSuperTypeEnum, ApplianceType
from app.v1.appliances.services.appliance_type import ApplianceTypesService
from app.v1.appliances.services.appliances import AppliancesService
from app.v1.auth.helpers.api_key_access_scopes_helper import APIKeyAccessScopesHelper
from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.auth.helpers.user_access_scopes_helper import UserAccessScopesHelper
from app.v1.auth.schemas.api_key import APIKey
from app.v1.auth.schemas.location_access_grant import LocationAccessGrant
from app.v1.auth.schemas.organization_access_grant import OrganizationAccessGrant
from app.v1.auth.schemas.user_location_access_grant import UserLocationAccessGrant
from app.v1.auth.schemas.user_organization_access_grant import UserOrganizationAccessGrant
from app.v1.auth.services.api_keys import APIKeysService
from app.v1.auth.services.user_location_access_grants import UserLocationAccessGrantsService
from app.v1.auth.services.user_organization_access_grants import UserOrganizationAccessGrantsService
from app.v1.dependencies import get_access_token_data, get_gateways_service, get_locations_service, get_user_access_grants_helper
from app.v1.electricity_dashboards.schemas.electricity_dashboard import ElectricityDashboard
from app.v1.electricity_dashboards.services.electricity_dashboards_service import ElectricityDashboardsService
from app.v1.electricity_monitoring.schemas.circuit import Circuit
from app.v1.electricity_monitoring.schemas.clamp import Clamp
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanel, ElectricPanelTypeEnum
from app.v1.electricity_monitoring.schemas.electric_sensor import ElectricSensor

from app.v1.electricity_monitoring.services.circuits import CircuitsService
from app.v1.electricity_monitoring.services.clamps import ClampsService
from app.v1.electricity_monitoring.services.electric_panels import ElectricPanelsService
from app.v1.electricity_monitoring.services.electric_sensors import ElectricSensorsService
from app.v1.hvac.schemas.hvac_equipment_type import HvacEquipmentType
from app.v1.hvac.schemas.hvac_zone_equipment import HvacZoneEquipment
from app.v1.hvac.schemas.hvac_zone_temperature_sensor import HvacZoneTemperatureSensor
from app.v1.hvac.schemas.hvac_zone import HvacZone
from app.v1.hvac.schemas.thermostat import Thermostat, ThermostatModelEnum
from app.v1.hvac.services.hvac_equipment_types import HvacEquipmentTypesService
from app.v1.hvac.services.hvac_zone_equipment import HvacZoneEquipmentService
from app.v1.hvac.services.hvac_zone_temperature_sensors import HvacZoneTemperatureSensorsService
from app.v1.hvac.services.hvac_zones import HvacZonesService
from app.v1.hvac.services.thermostats import ThermostatsService
from app.v1.hvac_dashboards.schemas.control_zone_hvac_widget import ControlZoneHvacWidget
from app.v1.hvac_dashboards.schemas.hvac_dashboard import HvacDashboard
from app.v1.hvac_dashboards.services.control_zone_hvac_widgets_service import ControlZoneHvacWidgetsService
from app.v1.hvac_dashboards.services.hvac_dashboards_service import HvacDashboardsService
from app.v1.locations.schemas.location import Location
from app.v1.locations.schemas.location_electricity_price import LocationElectricityPrice
from app.v1.locations.schemas.location_operating_hours import LocationOperatingHours, LocationOperatingHoursMap
from app.v1.locations.services.location_electricity_prices import LocationElectricityPricesService
from app.v1.locations.services.location_operating_hours import LocationOperatingHoursService
from app.v1.locations.services.locations import LocationsService
from app.v1.mesh_network.schemas.gateway import Gateway
from app.v1.mesh_network.schemas.node import Node
from app.v1.mesh_network.services.gateways import GatewaysService
from app.v1.mesh_network.services.nodes import NodesService
from app.v1.organizations.schemas.organization import Organization
from app.v1.organizations.schemas.organization_user import OrganizationUser
from app.v1.organizations.services.organization_users import OrganizationUsersService
from app.v1.organizations.services.organizations import OrganizationsService
from app.v1.schemas import AccessScope, DayOfWeek, AccessTokenData
from app.v1.temperature_dashboards.schemas.temperature_dashboard import TemperatureDashboard
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import TemperatureUnitWidget, ApplianceType as TemperatureUnitWidgetApplianceType
from app.v1.temperature_dashboards.services.temperature_dashboards_service import TemperatureDashboardsService
from app.v1.temperature_dashboards.services.temperature_unit_widgets_service import TemperatureUnitWidgetsService
from app.v1.temperature_monitoring.schemas.temperature_range import TemperatureRange, TemperatureRangeWarningLevelEnum
from app.v1.temperature_monitoring.schemas.temperature_sensor import TemperatureSensor
from app.v1.temperature_monitoring.schemas.temperature_sensor_place_alert import TemperatureSensorPlaceAlert, TemperatureSensorPlaceAlertType
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import TemperatureSensorPlace, TemperatureSensorPlaceType
from app.v1.temperature_monitoring.services.temperature_ranges import TemperatureRangesService
from app.v1.temperature_monitoring.services.temperature_sensor_place_alerts import TemperatureSensorPlaceAlertsService
from app.v1.temperature_monitoring.services.temperature_sensor_places import TemperatureSensorPlacesService
from app.v1.temperature_monitoring.services.temperature_sensors import TemperatureSensorsService
from app.v1.users.schemas.user import User
from app.sqlalchemy_session import SessionLocal
from app.database import Base
from app.main import app
from app.v1.users.services.users import UsersService


def clear_database(session: Session):
    meta = Base.metadata
    for table in reversed(meta.sorted_tables):
        session.execute(table.delete())
    session.commit()


@pytest.fixture(scope='function')
def db_session_for_tests():
    with SessionLocal() as session:
        clear_database(session)
        yield session
        session.rollback()
        clear_database(session)


_user = User(
    user_id=uuid4(),
    first_name='Lando',
    last_name='Norris',
    email='admin@powerx.co',
    password_hash='hashed_password',
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_organization = Organization(
    organization_id=uuid4(),
    name='Test Organization',
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_location = Location(
    location_id=uuid4(),
    name='Test Location',
    address='1234 Power St',
    city='Milwaukee',
    state='WI',
    zip_code='53212',
    country='USA',
    latitude=1.0,
    longitude=2.0,
    timezone='America/Chicago',
    organization_id=_organization.organization_id,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_location_operating_hours = LocationOperatingHours(
    location_id=_location.location_id,
    day_of_week=DayOfWeek.MONDAY,
    is_open=True,
    work_start_time=datetime.now().time(),
    open_time=datetime.now().time(),
    close_time=datetime.now().time(),
    work_end_time=datetime.now().time(),
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_location_operating_hours_list = [
    LocationOperatingHours(
        location_id=_location.location_id,
        day_of_week=day_of_week,
        is_open=True,
        work_start_time=datetime.now().time(),
        open_time=datetime.now().time(),
        close_time=datetime.now().time(),
        work_end_time=datetime.now().time(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    for day_of_week in DayOfWeek
]

_location_operating_hours_map = LocationOperatingHoursMap(**{
    location_operating_hours.day_of_week: location_operating_hours
    for location_operating_hours in _location_operating_hours_list
})

_location_electricity_price = LocationElectricityPrice(
    location_id=_location.location_id,
    comment='Initial price',
    price_per_kwh=0.123,
    started_at=datetime(2024, 1, 1),
    ended_at=None,
    location_electricity_price_id=uuid4(),
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_organization_user = OrganizationUser(
    organization_id=_organization.organization_id,
    is_organization_owner=False,
    user_id=_user.user_id,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_gateway = Gateway(
    gateway_id=uuid4(),
    name='Test Gateway',
    duid='test_duid',
    location_id=_location.location_id,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_node = Node(
    name='Test Node',
    duid='test_duid',
    gateway_id=_gateway.gateway_id,
    type='standard',
    node_id=uuid4(),
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_electric_panel_id = uuid4()

_circuits = [
    Circuit(
        circuit_id=uuid4(),
        name="Test Circuit 1",
        electric_panel_id=_electric_panel_id,
        type="main",
        created_at=datetime.now(),
        updated_at=datetime.now()
    ),
    Circuit(
        circuit_id=uuid4(),
        name="Test Circuit 2",
        electric_panel_id=_electric_panel_id,
        type="neutral",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
]

_electric_sensors = [
    ElectricSensor(
        electric_sensor_id=uuid4(),
        name="Test Electric Sensor 1",
        duid='aaaaaaaa',
        port_count=3,
        electric_panel_id=_electric_panel_id,
        gateway_id=_gateway.gateway_id,
        a_breaker_num=1,
        b_breaker_num=2,
        c_breaker_num=3,
        created_at=datetime.now(),
        updated_at=datetime.now()
    ),
    ElectricSensor(
        electric_sensor_id=uuid4(),
        name="Test Electric Sensor 2",
        duid='bbbbbbbb',
        port_count=3,
        electric_panel_id=_electric_panel_id,
        gateway_id=_gateway.gateway_id,
        a_breaker_num=4,
        b_breaker_num=5,
        c_breaker_num=6,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
]

_clamps = [
    Clamp(
        clamp_id=uuid4(),
        name="Test Clamp 1",
        port_name="Test Port 1",
        port_pin=1,
        amperage_rating=100,
        phase="A",
        circuit_id=_circuits[0].circuit_id,
        electric_sensor_id=_electric_sensors[0].electric_sensor_id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    ),
    Clamp(
        clamp_id=uuid4(),
        name="Test Clamp 2",
        port_name="Test Port 2",
        port_pin=2,
        amperage_rating=200,
        phase="B",
        circuit_id=_circuits[1].circuit_id,
        electric_sensor_id=_electric_sensors[1].electric_sensor_id,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
]

_electric_panel = ElectricPanel(
    name='Test Electric Panel',
    panel_type=ElectricPanelTypeEnum.mdp,
    location_id=_location.location_id,
    breaker_count=10,
    electric_panel_id=_electric_panel_id,
    parent_electric_panel_id=None,
    circuits=[],
    electric_sensors=[],
    clamps=[],
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_temperature_sensor = TemperatureSensor(
    name='Test Temperature Sensor',
    duid='test_duid',
    make='ruuvi',
    model='ruuvi_tag',
    gateway_id=_gateway.gateway_id,
    location_id=_location.location_id,
    temperature_sensor_id=uuid4(),
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_temperature_sensor_place = TemperatureSensorPlace(
    temperature_sensor_place_id=uuid4(),
    name='Test Temperature Sensor Place',
    temperature_sensor_place_type=TemperatureSensorPlaceType.APPLIANCE,
    location_id=_location.location_id,
    temperature_sensor_id=_temperature_sensor.temperature_sensor_id,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_temperature_sensor_place_alert = TemperatureSensorPlaceAlert(
    temperature_sensor_place_alert_id=uuid4(),
    temperature_sensor_place_id=_temperature_sensor_place.temperature_sensor_place_id,
    alert_type=TemperatureSensorPlaceAlertType.ABOVE_NORMAL_OPERATING_RANGE,
    threshold_temperature_c=20.0,
    threshold_window_seconds=300,
    reporter_temperature_c=25.0,
    started_at=datetime.now(),
    ended_at=None,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_temperature_range = TemperatureRange(
    high_degrees_celcius=30.0,
    low_degrees_celcius=20.0,
    warning_level=TemperatureRangeWarningLevelEnum.GOOD,
    temperature_sensor_place_id=_temperature_sensor_place.temperature_sensor_place_id,
    temperature_range_id=uuid4(),
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_hvac_equipment_type = HvacEquipmentType(
    hvac_equipment_type_id=uuid4(),
    make='Test Make',
    model='Test Model',
    type='Test Type',
    subtype='Test Subtype',
    year_manufactured=2021,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_hvac_zone = HvacZone(
    hvac_zone_id=uuid4(),
    name='Test HVAC Zone',
    location_id=_location.location_id,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_hvac_zone_equipment = HvacZoneEquipment(
    hvac_zone_equipment_id=uuid4(),
    hvac_zone_id=_hvac_zone.hvac_zone_id,
    circuit_id=_circuits[0].circuit_id,
    serial='test_serial',
    hvac_equipment_type_id=_hvac_equipment_type.hvac_equipment_type_id,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_hvac_zone_temperature_sensor = HvacZoneTemperatureSensor(
    hvac_zone_temperature_sensor_id=uuid4(),
    hvac_zone_id=_hvac_zone.hvac_zone_id,
    temperature_sensor_id=_temperature_sensor.temperature_sensor_id,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_thermostat = Thermostat(
    thermostat_id=uuid4(),
    name='Test Thermostat',
    duid='test_duid',
    modbus_address=0,
    model=ThermostatModelEnum.v1,
    node_id=_node.node_id,
    hvac_zone_id=_hvac_zone.hvac_zone_id,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_appliance_type = ApplianceType(
    appliance_type_id=uuid4(),
    make='Test Make',
    model='Test Model',
    type='Test Type',
    subtype='Test Subtype',
    year_manufactured=2021,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_appliance = Appliance(
    appliance_id=uuid4(),
    name='Test Appliance',
    appliance_super_type=ApplianceSuperTypeEnum.FRIDGE,
    appliance_type_id=_appliance_type.appliance_type_id,
    location_id=_location.location_id,
    circuit_id=_circuits[0].circuit_id,
    temperature_sensor_place_id=_temperature_sensor_place.temperature_sensor_place_id,
    serail='test_serial',
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_electricity_dashboard = ElectricityDashboard(    
    electricity_dashboard_id=uuid4(),
    name='Test Dashboard',
    location_id=_location.location_id,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_temperature_dashboard = TemperatureDashboard(
    temperature_dashboard_id=uuid4(),
    name='Test Dashboard',
    location_id=_location.location_id,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_temperature_unit_widget = TemperatureUnitWidget(
    temperature_unit_widget_id=uuid4(),
    name='Test Temperature Unit Widget',
    low_c=20.0,
    high_c=30.0,
    alert_threshold_s=300,
    appliance_type=TemperatureUnitWidgetApplianceType.FRIDGE,
    temperature_sensor_place_id=_temperature_sensor_place.temperature_sensor_place_id,
    temperature_dashboard_id=_temperature_dashboard.temperature_dashboard_id,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_hvac_dashboard = HvacDashboard(
    hvac_dashboard_id=uuid4(),
    name='Test Dashboard',
    location_id=_location.location_id,
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_control_zone_hvac_widget = ControlZoneHvacWidget(
    hvac_widget_id=uuid4(),
    name='Test Control Zone Hvac Widget',
    hvac_zone_id=_hvac_zone.hvac_zone_id,
    hvac_dashboard_id=_hvac_dashboard.hvac_dashboard_id,
    monday_schedule=None,
    tuesday_schedule=None,
    wednesday_schedule=None,
    thursday_schedule=None,
    friday_schedule=None,
    saturday_schedule=None,
    sunday_schedule=None,
    temperature_place_links=[],
    created_at=datetime.now(),
    updated_at=datetime.now()
)

_user_location_access_grants = [
    UserLocationAccessGrant(
        user_id=_user.user_id,
        location_id=_location.location_id,
        location_access_grant=location_access_grant,
        created_at=datetime.now(),
    )
    for location_access_grant in LocationAccessGrant
]

_user_organization_access_grants = [
    UserOrganizationAccessGrant(
        user_id=_user.user_id,
        organization_id=_organization.organization_id,
        organization_access_grant=organization_access_grant,
        created_at=datetime.now(),
    )
    for organization_access_grant in OrganizationAccessGrant
]

_api_key = APIKey(
    api_key_id=uuid4(),
    name='Test API Key',
    api_key_hash='hashed_api_key',
    created_at=datetime.now(),
    updated_at=datetime.now()
)

#
# Common data structures
#
@pytest.fixture
def user():
    return _user.model_copy(deep=True)

@pytest.fixture
def organization():
    return _organization.model_copy(deep=True)

@pytest.fixture
def location():
    return _location.model_copy(deep=True)

@pytest.fixture
def location_operating_hours():
    return _location_operating_hours.model_copy(deep=True)

@pytest.fixture
def location_operating_hours_list():
    return _location_operating_hours_list.copy()

@pytest.fixture
def location_operating_hours_map():
    return _location_operating_hours_map.model_copy(deep=True)

@pytest.fixture
def location_electricity_price():
    return _location_electricity_price.model_copy(deep=True)

@pytest.fixture
def organization_user():
    return _organization_user.model_copy(deep=True)

@pytest.fixture
def gateway():
    return _gateway.model_copy(deep=True)

@pytest.fixture
def node():
    return _node.model_copy(deep=True)

@pytest.fixture
def circuit():
    return _circuits[0].model_copy(deep=True)

@pytest.fixture
def circuits():
    return [ _circuit.model_copy(deep=True) for _circuit in _circuits ]

@pytest.fixture
def electric_sensor():
    return _electric_sensors[0].model_copy(deep=True)

@pytest.fixture
def electric_sensors():
    return [ _electric_sensor.model_copy(deep=True) for _electric_sensor in _electric_sensors ]

@pytest.fixture
def clamp():
    return _clamps[0].model_copy(deep=True)

@pytest.fixture
def clamps():
    return [ _clamp.model_copy(deep=True) for _clamp in _clamps ]

@pytest.fixture
def electric_panel():
    return _electric_panel.model_copy(deep=True)

@pytest.fixture
def appliance_type():
    return _appliance_type.model_copy(deep=True)

@pytest.fixture
def appliance():
    return _appliance.model_copy(deep=True)

@pytest.fixture
def temperature_sensor():
    return _temperature_sensor.model_copy(deep=True)

@pytest.fixture
def temperature_sensor_place():
    return _temperature_sensor_place.model_copy(deep=True)

@pytest.fixture
def temperature_sensor_place_alert():
    return _temperature_sensor_place_alert.model_copy(deep=True)

@pytest.fixture
def temperature_range():
    return _temperature_range.model_copy(deep=True)

@pytest.fixture
def hvac_equipment_type():
    return _hvac_equipment_type.model_copy(deep=True)

@pytest.fixture
def hvac_zone():
    return _hvac_zone.model_copy(deep=True)

@pytest.fixture
def hvac_zone_equipment():
    return _hvac_zone_equipment.model_copy(deep=True)

@pytest.fixture
def hvac_zone_temperature_sensor():
    return _hvac_zone_temperature_sensor.model_copy(deep=True)

@pytest.fixture
def thermostat():
    return _thermostat.model_copy(deep=True)

@pytest.fixture
def user_location_access_grants():
    return [ _user_location_access_grant.model_copy(deep=True) for _user_location_access_grant in _user_location_access_grants ]

@pytest.fixture
def user_organization_access_grants():
    return [ _user_organization_access_grant.model_copy(deep=True) for _user_organization_access_grant in _user_organization_access_grants ]

@pytest.fixture
def electricity_dashboard():
    return _electricity_dashboard.model_copy(deep=True)

@pytest.fixture
def temperature_dashboard():
    return _temperature_dashboard.model_copy(deep=True)

@pytest.fixture
def temperature_unit_widget():
    return _temperature_unit_widget.model_copy(deep=True)

@pytest.fixture
def hvac_dashboard():
    return _hvac_dashboard.model_copy(deep=True)

@pytest.fixture
def control_zone_hvac_widget():
    return _control_zone_hvac_widget.model_copy(deep=True)

@pytest.fixture
def api_key():
    return _api_key.model_copy(deep=True)
#
# TokenData w/ varying access levels
#
@pytest.fixture
def token_data_with_access_scope(user: User,
                                 organization: Organization,
                                 location: Location):
    def _token_data_with_access_scope(access_scope: Optional[AccessScope]):
        return AccessTokenData(
            user_id=user.user_id,
            given_name=user.first_name,
            family_name=user.last_name,
            email=user.email,
            access_scopes=[access_scope] if access_scope else [],
            organization_ids=[organization.organization_id],
            location_ids=[location.location_id],
            exp=datetime.now() + timedelta(days=1)
        )
    return _token_data_with_access_scope

@pytest.fixture
def token_data_with_access_scopes(user: User,
                                  organization: Organization,
                                  location: Location):
    def _token_data_with_access_scopes(access_scopes: List[AccessScope]):
        return AccessTokenData(
            user_id=user.user_id,
            given_name=user.first_name,
            family_name=user.last_name,
            email=user.email,
            access_scopes=access_scopes,
            exp=datetime.now() + timedelta(days=1)
        )
    return _token_data_with_access_scopes

@pytest.fixture
def admin_all_access_token_data(user: User):
    return AccessTokenData(
        user_id=user.user_id,
        given_name=user.first_name,
        family_name=user.last_name,
        email=user.email,
        access_scopes=[
            access_scope for access_scope in AccessScope
        ],
        exp=datetime.now() + timedelta(days=1)
    )

@pytest.fixture
def admin_read_access_token_data(user: User):
    return AccessTokenData(
        user_id=user.user_id,
        given_name=user.first_name,
        family_name=user.last_name,
        email=user.email,
        access_scopes=[
            access_scope for access_scope in AccessScope if access_scope.value.split(":")[1].lower() == "write"
        ],
        exp=datetime.now() + timedelta(days=1)
    )

@pytest.fixture
def all_access_token_data(user: User,
                          organization: Organization,
                          location: Location):
    return AccessTokenData(
        user_id=user.user_id,
        given_name=user.first_name,
        family_name=user.last_name,
        email=user.email,
        access_scopes=[
            access_scope for access_scope in AccessScope if access_scope not in [AccessScope.ADMIN]
        ],
        exp=datetime.now() + timedelta(days=1)
    )

@pytest.fixture
def read_access_token_data(user: User,
                           organization: Organization,
                           location: Location):
    return AccessTokenData(
        user_id=user.user_id,
        given_name=user.first_name,
        family_name=user.last_name,
        email=user.email,
        access_scopes=[
            access_scope for access_scope in AccessScope if access_scope.value.split(":")[1].lower() == "read"
        ],
        exp=datetime.now() + timedelta(days=1)
    )

@pytest.fixture
def no_access_token_data(user: User,
                         organization: Organization,
                         location: Location):
    return AccessTokenData(
        user_id=user.user_id,
        given_name=user.first_name,
        family_name=user.last_name,
        email=user.email,
        access_scopes=[],
        exp=datetime.now() + timedelta(days=1)
    )

#
# Helpers
#
@pytest.fixture
def user_access_scopes_helper_mock():
    user_access_scopes_helper_mock = Mock(spec_set=UserAccessScopesHelper)
    user_access_scopes_helper_mock.get_all_access_scopes_for_user.return_value = [AccessScope.ADMIN]
    return user_access_scopes_helper_mock

#
# Services
#
@pytest.fixture
def users_service_mock(user: User):
    users_service_mock = Mock(spec_set=UsersService)
    users_service_mock.get_user_by_email.return_value = user
    users_service_mock.get_user_by_user_id.return_value = user
    users_service_mock.create_user.return_value = user
    return users_service_mock

@pytest.fixture
def organizations_service_mock(organization: Organization):
    organizations_service_mock = Mock(spec_set=OrganizationsService)
    organizations_service_mock.create_organization.return_value = organization
    organizations_service_mock.get_organizations.return_value = [organization,]
    organizations_service_mock.get_organization_by_organization_id.return_value = organization
    organizations_service_mock.get_organization_by_name.return_value = organization
    return organizations_service_mock

@pytest.fixture
def organization_users_service_mock(organization_user: OrganizationUser):
    organization_users_service_mock = Mock(spec_set=OrganizationUsersService)
    organization_users_service_mock.create_organization_user.return_value = organization_user
    organization_users_service_mock.get_organization_users.return_value = [organization_user,]
    organization_users_service_mock.get_organization_user.return_value = organization_user
    return organization_users_service_mock

@pytest.fixture
def gateways_service_mock(gateway: Gateway):
    gateways_service_mock = Mock(spec_set=GatewaysService)
    gateways_service_mock.create_gateway.return_value = gateway
    gateways_service_mock.get_gateways_by_location_id.return_value = [gateway,]
    gateways_service_mock.get_gateway_by_gateway_id.return_value = gateway
    return gateways_service_mock

@pytest.fixture
def nodes_service_mock(node: Node):
    nodes_service_mock = Mock(spec_set=NodesService)
    nodes_service_mock.create_node.return_value = node
    nodes_service_mock.get_nodes_by_gateway_id.return_value = [node,]
    nodes_service_mock.get_node_by_node_id.return_value = node
    nodes_service_mock.get_node_for_gateway_by_node_id.return_value = node
    return nodes_service_mock

@pytest.fixture
def locations_service_mock(location: Location):
    locations_service_mock = Mock(spec_set=LocationsService)
    locations_service_mock.create_location.return_value = location
    locations_service_mock.get_locations_by_organization_id.return_value = [location,]
    locations_service_mock.get_location.return_value = location
    return locations_service_mock

@pytest.fixture
def location_operating_hours_service_mock(location_operating_hours: LocationOperatingHours):
    location_operating_hours_service_mock = Mock(spec_set=LocationOperatingHoursService)
    location_operating_hours_service_mock.create_location_operating_hours.return_value = location_operating_hours
    location_operating_hours_service_mock.get_location_operating_hours_for_location.return_value = [location_operating_hours, ]
    location_operating_hours_service_mock.update_location_operating_hours.return_value = location_operating_hours
    location_operating_hours_service_mock.delete_location_operating_hours_for_location.return_value = None
    return location_operating_hours_service_mock

@pytest.fixture
def location_electricity_prices_service_mock(location_electricity_price: LocationElectricityPrice):
    location_electricity_prices_service_mock = Mock(spec_set=LocationElectricityPricesService)
    location_electricity_prices_service_mock.create_location_electricity_price.return_value = location_electricity_price
    location_electricity_prices_service_mock.update_location_electricity_price.return_value = location_electricity_price
    location_electricity_prices_service_mock.get_current_location_electricity_price.return_value = location_electricity_price
    location_electricity_prices_service_mock.get_location_electricity_prices.return_value = [location_electricity_price,]
    location_electricity_prices_service_mock.filter_by.return_value = [location_electricity_price,]
    return location_electricity_prices_service_mock

@pytest.fixture
def circuits_service_mock(circuit: Circuit):
    circuits_service_mock = Mock(spec_set=CircuitsService)
    circuits_service_mock.create_circuit.return_value = circuit
    circuits_service_mock.get_circuit_by_id.return_value = circuit
    circuits_service_mock.get_circuit_by_attributes.return_value = circuit
    circuits_service_mock.get_circuits_by_electric_panel.return_value = [circuit,]
    circuits_service_mock.filter_by.return_value = [circuit,]
    circuits_service_mock.delete_circuit.return_value = None
    return circuits_service_mock

@pytest.fixture
def electric_sensors_service_mock(electric_sensor: ElectricSensor):
    electric_sensors_service_mock = Mock(spec_set=ElectricSensorsService)
    electric_sensors_service_mock.create_electric_sensor.return_value = electric_sensor
    electric_sensors_service_mock.get_electric_sensor_by_id.return_value = electric_sensor
    electric_sensors_service_mock.get_electric_sensor_by_attributes.return_value = electric_sensor
    electric_sensors_service_mock.get_electric_sensors_by_gateway.return_value = [electric_sensor,]
    electric_sensors_service_mock.filter_by.return_value = [electric_sensor,]
    electric_sensors_service_mock.delete_electric_sensor.return_value = None
    return electric_sensors_service_mock

@pytest.fixture
def clamps_service_mock(clamp: Clamp):
    clamps_service_mock = Mock(spec_set=ClampsService)
    clamps_service_mock.create_clamp.return_value = clamp
    clamps_service_mock.get_clamp_by_id.return_value = clamp
    clamps_service_mock.get_clamp_by_attributes.return_value = clamp
    clamps_service_mock.get_clamps_by_circuit.return_value = [clamp,]
    clamps_service_mock.filter_by.return_value = [clamp,]
    clamps_service_mock.delete_clamp.return_value = None
    return clamps_service_mock

@pytest.fixture
def electric_panels_service_mock(electric_panel: ElectricPanel):
    electric_panels_service_mock = Mock(spec_set=ElectricPanelsService)
    electric_panels_service_mock.create_electric_panel.return_value = electric_panel
    electric_panels_service_mock.get_electric_panel_by_id.return_value = electric_panel
    electric_panels_service_mock.get_electric_panel_by_attributes.return_value = electric_panel
    electric_panels_service_mock.get_electric_panels_by_location.return_value = [electric_panel,]
    electric_panels_service_mock.filter_by.return_value = [electric_panel,]
    electric_panels_service_mock.delete_electric_panel.return_value = None
    return electric_panels_service_mock

@pytest.fixture
def appliance_types_service_mock(appliance_type: ApplianceType):
    appliance_types_service_mock = Mock(spec_set=ApplianceTypesService)
    appliance_types_service_mock.create_appliance_type.return_value = appliance_type
    appliance_types_service_mock.get_appliance_type_by_id.return_value = appliance_type
    appliance_types_service_mock.get_appliance_by_make_model_type_subtype_year.return_value = appliance_type
    appliance_types_service_mock.delete_appliance_type.return_value = None
    return appliance_types_service_mock

@pytest.fixture
def appliances_service_mock(appliance: Appliance):
    appliances_service_mock = Mock(spec_set=AppliancesService)
    appliances_service_mock.create_appliance.return_value = appliance
    appliances_service_mock.get_appliances_by_location.return_value = [appliance,]
    appliances_service_mock.get_appliance_by_id.return_value = appliance
    appliances_service_mock.get_appliance_by_attributes.return_value = appliance
    appliances_service_mock.delete_appliance.return_value = None
    return appliances_service_mock

@pytest.fixture
def temperature_sensors_service_mock(temperature_sensor: TemperatureSensor):
    temperature_sensors_service_mock = Mock(spec_set=TemperatureSensorsService)
    temperature_sensors_service_mock.create_temperature_sensor.return_value = temperature_sensor
    temperature_sensors_service_mock.get_temperature_sensors_by_location_id.return_value = [temperature_sensor,]
    temperature_sensors_service_mock.get_temperature_sensor_by_id.return_value = temperature_sensor
    temperature_sensors_service_mock.delete_temperature_sensor.return_value = None
    return temperature_sensors_service_mock

@pytest.fixture
def temperature_sensor_places_service_mock(temperature_sensor_place: TemperatureSensorPlace):
    temperature_sensor_places_service_mock = Mock(spec_set=TemperatureSensorPlacesService)
    temperature_sensor_places_service_mock.create_temperature_sensor_place.return_value = temperature_sensor_place
    temperature_sensor_places_service_mock.get_temperature_sensor_places.return_value = [temperature_sensor_place,]
    temperature_sensor_places_service_mock.get_temperature_sensor_place.return_value = temperature_sensor_place
    temperature_sensor_places_service_mock.delete_temperature_sensor_place.return_value = None
    return temperature_sensor_places_service_mock

@pytest.fixture
def temperature_sensor_place_alerts_service_mock(temperature_sensor_place_alert: TemperatureSensorPlaceAlert):
    temperature_sensor_place_alerts_service_mock = Mock(spec_set=TemperatureSensorPlaceAlertsService)
    temperature_sensor_place_alerts_service_mock.create_temperature_sensor_place_alert.return_value = temperature_sensor_place_alert
    temperature_sensor_place_alerts_service_mock.get_temperature_sensor_place_alerts_for_temperature_sensor_place.return_value = [temperature_sensor_place_alert,]
    temperature_sensor_place_alerts_service_mock.get_temperature_sensor_place_alert_for_temperature_sensor_place.return_value = temperature_sensor_place_alert
    temperature_sensor_place_alerts_service_mock.delete_temperature_sensor_place_alert.return_value = None
    return temperature_sensor_place_alerts_service_mock

@pytest.fixture
def temperature_ranges_service_mock(temperature_range: TemperatureRange):
    temperature_ranges_service_mock = Mock(spec_set=TemperatureRangesService)
    temperature_ranges_service_mock.create_temperature_range.return_value = temperature_range
    temperature_ranges_service_mock.get_temperature_ranges_by_temperature_sensor_place_id.return_value = [temperature_range,]
    temperature_ranges_service_mock.get_temperature_range_by_id.return_value = temperature_range
    temperature_ranges_service_mock.get_temperature_range_for_temperature_sensor_place_by_id.return_value = temperature_range
    temperature_ranges_service_mock.delete_temperature_range_by_id.return_value = None
    return temperature_ranges_service_mock

@pytest.fixture
def hvac_equipment_types_service_mock(hvac_equipment_type: HvacEquipmentType):
    hvac_equipment_types_service_mock = Mock(spec_set=HvacEquipmentTypesService)
    hvac_equipment_types_service_mock.create_hvac_equipment_type.return_value = hvac_equipment_type
    hvac_equipment_types_service_mock.get_hvac_equipment_type_by_id.return_value = hvac_equipment_type
    hvac_equipment_types_service_mock.get_hvac_equipment_type_by_make_model_type_subtype_year.return_value = hvac_equipment_type
    hvac_equipment_types_service_mock.delete_hvac_equipment_type.return_value = None
    return hvac_equipment_types_service_mock

@pytest.fixture
def hvac_zones_service_mock(hvac_zone: HvacZone):
    hvac_zones_service_mock = Mock(spec_set=HvacZonesService)
    hvac_zones_service_mock.create_hvac_zone.return_value = hvac_zone
    hvac_zones_service_mock.get_hvac_zone_by_attributes.return_value = hvac_zone
    hvac_zones_service_mock.get_hvac_zones_by_location_id.return_value = [hvac_zone,]
    hvac_zones_service_mock.get_hvac_zone_by_id.return_value = hvac_zone
    hvac_zones_service_mock.filter_by.return_value = [hvac_zone,]
    hvac_zones_service_mock.delete_hvac_zone.return_value = None
    return hvac_zones_service_mock

@pytest.fixture
def hvac_zone_equipment_service_mock(hvac_zone_equipment: HvacZoneEquipment):
    hvac_zone_equipment_service_mock = Mock(spec_set=HvacZoneEquipmentService)
    hvac_zone_equipment_service_mock.create_hvac_zone_equipment.return_value = hvac_zone_equipment
    hvac_zone_equipment_service_mock.get_hvac_zone_equipment_by_id.return_value = hvac_zone_equipment
    hvac_zone_equipment_service_mock.get_hvac_zone_equipment_by_attributes.return_value = hvac_zone_equipment
    hvac_zone_equipment_service_mock.get_hvac_zone_equipment_by_hvac_zone_id.return_value = [hvac_zone_equipment,]
    hvac_zone_equipment_service_mock.delete_hvac_zone_equipment.return_value = None
    return hvac_zone_equipment_service_mock

@pytest.fixture
def hvac_zone_temperature_sensors_service_mock(hvac_zone_temperature_sensor: HvacZoneTemperatureSensor):
    hvac_zone_temperature_sensors_service_mock = Mock(spec_set=HvacZoneTemperatureSensorsService)
    hvac_zone_temperature_sensors_service_mock.create_hvac_zone_temperature_sensor.return_value = hvac_zone_temperature_sensor
    hvac_zone_temperature_sensors_service_mock.get_hvac_zone_temperature_sensor_by_id.return_value = hvac_zone_temperature_sensor
    hvac_zone_temperature_sensors_service_mock.get_hvac_zone_temperature_sensor_by_attributes.return_value = hvac_zone_temperature_sensor
    hvac_zone_temperature_sensors_service_mock.get_hvac_zone_temperature_sensors_by_hvac_zone_id.return_value = [hvac_zone_temperature_sensor,]
    hvac_zone_temperature_sensors_service_mock.delete_hvac_zone_temperature_sensor.return_value = None
    return hvac_zone_temperature_sensors_service_mock

@pytest.fixture
def thermostats_service_mock(thermostat: Thermostat):
    thermostats_service_mock = Mock(spec_set=ThermostatsService)
    thermostats_service_mock.create_thermostat.return_value = thermostat
    thermostats_service_mock.get_thermostat_by_attributes.return_value = thermostat
    thermostats_service_mock.get_thermostat_by_id.return_value = thermostat
    thermostats_service_mock.delete_thermostat.return_value = None
    thermostats_service_mock.filter_by.return_value = [thermostat,]
    return thermostats_service_mock

@pytest.fixture
def electricity_dashboards_service_mock(electricity_dashboard: ElectricityDashboard):
    electricity_dashboards_service_mock = Mock(spec_set=ElectricityDashboardsService)
    electricity_dashboards_service_mock.create_electricity_dashboard.return_value = electricity_dashboard
    electricity_dashboards_service_mock.get_electricity_dashboard.return_value = electricity_dashboard
    electricity_dashboards_service_mock.filter_by.return_value = [electricity_dashboard,]
    return electricity_dashboards_service_mock

@pytest.fixture
def temperature_dashboards_service_mock(temperature_dashboard: TemperatureDashboard):
    temperature_dashboards_service_mock = Mock(spec_set=TemperatureDashboardsService)
    temperature_dashboards_service_mock.create_temperature_dashboard.return_value = temperature_dashboard
    temperature_dashboards_service_mock.get_temperature_dashboard.return_value = temperature_dashboard
    temperature_dashboards_service_mock.get_temperature_dashboards_for_location.return_value = [temperature_dashboard,]
    temperature_dashboards_service_mock.filter_by.return_value = [temperature_dashboard,]
    return temperature_dashboards_service_mock

@pytest.fixture
def temperature_unit_widgets_service_mock(temperature_unit_widget: TemperatureUnitWidget):
    temperature_unit_widgets_service_mock = Mock(spec_set=TemperatureUnitWidgetsService)
    temperature_unit_widgets_service_mock.create_temperature_unit_widget.return_value = temperature_unit_widget
    temperature_unit_widgets_service_mock.get_temperature_unit_widget.return_value = temperature_unit_widget
    temperature_unit_widgets_service_mock.get_temperature_unit_widgets_for_temperature_dashboard.return_value = [temperature_unit_widget,]
    temperature_unit_widgets_service_mock.filter_by.return_value = [temperature_unit_widget,]
    temperature_unit_widgets_service_mock.update_temperature_unit_widget = temperature_unit_widget
    return temperature_unit_widgets_service_mock

@pytest.fixture
def hvac_dashboards_service_mock(hvac_dashboard: HvacDashboard):
    hvac_dashboards_service_mock = Mock(spec_set=HvacDashboardsService)
    hvac_dashboards_service_mock.create_hvac_dashboard.return_value = hvac_dashboard
    hvac_dashboards_service_mock.get_hvac_dashboard.return_value = hvac_dashboard
    hvac_dashboards_service_mock.get_hvac_dashboards_for_location.return_value = [hvac_dashboard,]
    hvac_dashboards_service_mock.filter_by.return_value = [hvac_dashboard,]
    return hvac_dashboards_service_mock

@pytest.fixture
def control_zone_hvac_widgets_service_mock(control_zone_hvac_widget: ControlZoneHvacWidget):
    control_zone_hvac_widgets_service_mock = Mock(spec_set=ControlZoneHvacWidgetsService)
    control_zone_hvac_widgets_service_mock.create_control_zone_hvac_widget.return_value = control_zone_hvac_widget
    control_zone_hvac_widgets_service_mock.get_control_zone_hvac_widget.return_value = control_zone_hvac_widget
    control_zone_hvac_widgets_service_mock.update_control_zone_hvac_widget.return_value = control_zone_hvac_widget
    control_zone_hvac_widgets_service_mock.get_control_zone_hvac_widgets_with_schedule.return_value = [control_zone_hvac_widget,]
    control_zone_hvac_widgets_service_mock.get_control_zone_hvac_widgets_for_hvac_dashboard.return_value = [control_zone_hvac_widget,]
    control_zone_hvac_widgets_service_mock.get_control_zone_hvac_widgets_for_location.return_value = [control_zone_hvac_widget,]
    control_zone_hvac_widgets_service_mock.filter_by.return_value = [control_zone_hvac_widget,]
    return control_zone_hvac_widgets_service_mock

@pytest.fixture
def user_location_access_grants_service_mock(user_location_access_grants: List[UserLocationAccessGrant]):
    user_location_access_grants_service_mock = Mock(spec_set=UserLocationAccessGrantsService)
    user_location_access_grants_service_mock.add_user_location_access_grant.return_value = user_location_access_grants[0]
    user_location_access_grants_service_mock.add_user_location_access_grants.return_value = user_location_access_grants
    user_location_access_grants_service_mock.get_user_location_access_grants.return_value = user_location_access_grants
    user_location_access_grants_service_mock.get_user_location_access_grants_for_location.return_value = user_location_access_grants
    user_location_access_grants_service_mock.set_user_location_access_grants_for_location.return_value = user_location_access_grants
    user_location_access_grants_service_mock.remove_user_location_access_grant.return_value = None
    user_location_access_grants_service_mock.remove_user_location_access_grants.return_value = None
    return user_location_access_grants_service_mock

@pytest.fixture
def user_organization_access_grants_service_mock(user_organization_access_grants: List[UserOrganizationAccessGrant]):
    user_organization_access_grants_service_mock = Mock(spec_set=UserOrganizationAccessGrantsService)
    user_organization_access_grants_service_mock.add_user_organization_access_grant.return_value = user_organization_access_grants[0]
    user_organization_access_grants_service_mock.add_user_organization_access_grants.return_value = user_organization_access_grants
    user_organization_access_grants_service_mock.get_user_organization_access_grants.return_value = user_organization_access_grants
    user_organization_access_grants_service_mock.set_user_organization_access_grants.return_value = user_organization_access_grants
    user_organization_access_grants_service_mock.get_user_organization_access_grants_for_organization.return_value = user_organization_access_grants
    user_organization_access_grants_service_mock.remove_user_organization_access_grant.return_value = None
    user_organization_access_grants_service_mock.remove_user_organization_access_grants.return_value = None
    return user_organization_access_grants_service_mock

@pytest.fixture
def api_keys_service_mock(api_key: APIKey):
    api_keys_service_mock = Mock(spec_set=APIKeysService)
    api_keys_service_mock.create_api_key.return_value = api_key
    api_keys_service_mock.get_api_key.return_value = api_key
    return api_keys_service_mock

@pytest.fixture
def user_access_grants_helper_mock():
    return Mock(spec_set=UserAccessGrantsHelper)

@pytest.fixture
def api_key_access_scopes_helper_mock():
    return Mock(spec_set=APIKeyAccessScopesHelper)

@pytest.fixture(scope='function', autouse=True)
def clear_dependency_overrides(locations_service_mock,
                               user_access_grants_helper_mock,
                               gateways_service_mock):
    app.dependency_overrides = {}
    app.dependency_overrides[get_access_token_data] = get_access_token_data
    app.dependency_overrides[get_locations_service] = lambda: locations_service_mock
    app.dependency_overrides[get_user_access_grants_helper] = lambda: user_access_grants_helper_mock
    app.dependency_overrides[get_gateways_service] = lambda: gateways_service_mock
    yield
    app.dependency_overrides = {}