import logging
import os

from typing import Any, Generator, List, Optional

import boto3
import jwt

from dotenv import load_dotenv
from fastapi import HTTPException, Security, status, Depends, Request
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.orm import Session
from mypy_boto3_s3 import S3Client

from app.sqlalchemy_session import SessionLocal
from app.v1.appliances.repositories.appliance_types_repository import PostgresApplianceTypesRepository
from app.v1.appliances.repositories.appliances_repository import PostgresAppliancesRepository
from app.v1.appliances.services.appliance_type import ApplianceTypesService
from app.v1.appliances.services.appliances import AppliancesService
from app.v1.auth.helpers.api_key_access_scopes_helper import APIKeyAccessScopesHelper
from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.auth.helpers.user_access_scopes_helper import UserAccessScopesHelper
from app.v1.auth.repositories.access_role_access_scopes_repository import PostgresAccessRoleAccessScopesRepository
from app.v1.auth.repositories.api_key_access_roles_repository import PostgresAPIKeyAccessRolesRepository
from app.v1.auth.repositories.api_key_access_scopes_repository import PostgresAPIKeyAccessScopesRepository
from app.v1.auth.repositories.api_keys_repository import PostgresAPIKeysRepository
from app.v1.auth.repositories.user_access_roles_repository import PostgresUserAccessRolesRepository
from app.v1.auth.repositories.user_access_scopes_repository import PostgresUserAccessScopesRepository
from app.v1.auth.repositories.user_location_access_grants_repository import PostgresUserLocationAccessGrantsRepository
from app.v1.auth.repositories.user_organization_access_grants_repository import PostgresUserOrganizationAccessGrantsRepository
from app.v1.auth.repositories.access_roles_repository import PostgresAccessRolesRepository
from app.v1.auth.schemas.api_key import APIKey
from app.v1.auth.services.access_role_access_scopes import AccessRoleAccessScopesService
from app.v1.auth.services.api_key_access_roles import APIKeyAccessRolesService
from app.v1.auth.services.api_key_access_scopes import APIKeyAccessScopesService
from app.v1.auth.services.api_keys import APIKeysService
from app.v1.auth.services.user_access_roles import UserAccessRolesService
from app.v1.auth.services.user_access_scopes import UserAccessScopesService
from app.v1.auth.services.user_location_access_grants import UserLocationAccessGrantsService
from app.v1.auth.services.user_organization_access_grants import UserOrganizationAccessGrantsService
from app.v1.auth.services.access_roles import AccessRolesService
from app.v1.cache.cache import Cache
from app.v1.cache.redis_cache import RedisCache
from app.v1.dp_pes.client import DpPesClient
from app.v1.dp_pes.service import DpPesService
from app.v1.electricity_dashboards.repositories.electricity_dashboards_repository import PostgresElectricityDashboardsRepository
from app.v1.electricity_dashboards.repositories.energy_consumption_breakdown_electric_widgets_repository import PostgresEnergyConsumptionBreakdownElectricWidgetRepository
from app.v1.electricity_dashboards.repositories.energy_load_curve_electric_widgets_repository import PostgresEnergyLoadCurveElectricWidgetsRepository
from app.v1.electricity_dashboards.repositories.panel_system_health_electric_widgets_repository import PostgresPanelSystemHealthElectricWidgetsRepository
from app.v1.electricity_dashboards.services.electricity_dashboards_service import ElectricityDashboardsService
from app.v1.electricity_dashboards.services.energy_consumption_breakdown_electric_widgets_service import EnergyConsumptionBreakdownElectricWidgetsService
from app.v1.electricity_dashboards.services.energy_load_curve_electric_widgets_service import EnergyLoadCurveElectricWidgetsService
from app.v1.electricity_dashboards.services.panel_system_health_electric_widgets_service import PanelSystemHealthElectricWidgetsService
from app.v1.electricity_monitoring.repositories.circuits_repository import PostgresCircuitsRepository
from app.v1.electricity_monitoring.repositories.clamps_repository import PostgresClampsRepository
from app.v1.electricity_monitoring.repositories.electric_panels_repository import PostgresElectricPanelsRepository
from app.v1.electricity_monitoring.repositories.electric_sensors_repository import PostgresElectricSensorsRepository
from app.v1.electricity_monitoring.services.circuits import CircuitsService
from app.v1.electricity_monitoring.services.clamps import ClampsService
from app.v1.electricity_monitoring.services.electric_panels import ElectricPanelsService
from app.v1.electricity_monitoring.services.electric_sensors import ElectricSensorsService
from app.v1.hvac.repositories.hvac_equipment_types_repository import PostgresHvacEquipmentTypesRepository
from app.v1.hvac.repositories.hvac_holds_repository import PostgresHvacHoldsRepository
from app.v1.hvac.repositories.hvac_schedules_repository import PostgresHvacSchedulesRepository
from app.v1.hvac.repositories.hvac_zone_equipment_repository import PostgresHvacZoneEquipmentRepository
from app.v1.hvac.repositories.hvac_zone_temperature_sensors_repository import PostgresHvacZoneTemperatureSensorsRepository
from app.v1.hvac.repositories.hvac_zones_repository import PostgresHvacZonesRepository
from app.v1.hvac.repositories.thermostats_repository import PostgresThermostatsRepository
from app.v1.hvac.services.hvac_equipment_types import HvacEquipmentTypesService
from app.v1.hvac.services.hvac_holds import HvacHoldsService
from app.v1.hvac.services.hvac_schedules import HvacSchedulesService
from app.v1.hvac.services.hvac_zone_equipment import HvacZoneEquipmentService
from app.v1.hvac.services.hvac_zone_temperature_sensors import HvacZoneTemperatureSensorsService
from app.v1.hvac.services.hvac_zones import HvacZonesService
from app.v1.hvac.services.thermostats import ThermostatsService
from app.v1.hvac_dashboards.repositories.control_zone_hvac_widgets_repository import PostgresControlZoneHvacWidgetsRepository
from app.v1.hvac_dashboards.repositories.control_zone_temperature_place_links_repository import PostgresControlZoneTemperaturePlaceLinksRepository
from app.v1.hvac_dashboards.repositories.hvac_dashboards_repository import PostgresHvacDashboardsRepository
from app.v1.hvac_dashboards.services.control_zone_hvac_widgets_service import ControlZoneHvacWidgetsService
from app.v1.hvac_dashboards.services.hvac_dashboards_service import HvacDashboardsService
from app.v1.locations.repositories.location_electricity_prices_repository import PostgresLocationElectricityPricesRepository
from app.v1.locations.repositories.location_operating_hours_repository import PostgresLocationOperatingHoursRepository
from app.v1.locations.repositories.location_time_of_use_rates_repository import PostgresLocationTimeOfUseRatesRepository
from app.v1.locations.repositories.locations_repository import PostgresLocationsRepository
from app.v1.locations.services.location_electricity_prices import LocationElectricityPricesService
from app.v1.locations.services.location_operating_hours import LocationOperatingHoursService
from app.v1.locations.services.location_time_of_use_rates import LocationTimeOfUseRatesService
from app.v1.locations.services.locations import LocationsService
from app.v1.mesh_network.repositories.gateways_repository import PostgresGatewaysRepository
from app.v1.mesh_network.repositories.nodes_repository import PostgresNodesRepository
from app.v1.mesh_network.services.gateways import GatewaysService
from app.v1.mesh_network.services.nodes import NodesService
from app.v1.organizations.repositories.organization_feature_toggles_repository import PostgresOrganizationFeatureTogglesRepository
from app.v1.organizations.repositories.organization_users_repository import PostgresOrganizationUsersRepository
from app.v1.organizations.repositories.organizations_repository import PostgresOrganizationsRepository
from app.v1.organizations.services.organization_feature_toggles import OrganizationFeatureTogglesService
from app.v1.organizations.services.organization_logos import OrganizationLogosService
from app.v1.organizations.services.organization_users import OrganizationUsersService
from app.v1.organizations.services.organizations import OrganizationsService
from app.v1.schemas import AccessScope, RefreshTokenData, AccessTokenData, ACCESS_SCOPE_TO_DEFINITION
from app.v1.devices.repositories.location_devices_repository import LocationDevicesRepository, PostgresLocationDevicesRepository
from app.v1.devices.services.device_status_service import DeviceStatusService
from app.v1.temperature_dashboards.repositories.temperature_dashboards_repository import PostgresTemperatureDashboardsRepository
from app.v1.temperature_dashboards.repositories.temperature_unit_widgets_repository import PostgresTemperatureUnitWidgetsRepository
from app.v1.temperature_dashboards.services.temperature_dashboards_service import TemperatureDashboardsService
from app.v1.temperature_dashboards.services.temperature_unit_widgets_service import TemperatureUnitWidgetsService
from app.v1.temperature_monitoring.repositories.temperature_ranges_repository import PostgresTemperatureRangesRepository
from app.v1.temperature_monitoring.repositories.temperature_sensor_place_alerts_repository import PostgresTemperatureSensorPlaceAlertsRepository
from app.v1.temperature_monitoring.repositories.temperature_sensor_place_readings_repository import CacheTemperatureSensorPlaceReadingsRepository
from app.v1.temperature_monitoring.repositories.temperature_sensor_places_repository import PostgresTemperatureSensorPlacesRepository
from app.v1.temperature_monitoring.repositories.temperature_sensors_repository import PostgresTemperatureSensorsRepository
from app.v1.temperature_monitoring.services.temperature_ranges import TemperatureRangesService
from app.v1.temperature_monitoring.services.temperature_sensor_place_alerts import TemperatureSensorPlaceAlertsService
from app.v1.temperature_monitoring.services.temperature_sensor_place_readings import TemperatureSensorPlaceReadingsService
from app.v1.temperature_monitoring.services.temperature_sensor_places import TemperatureSensorPlacesService
from app.v1.temperature_monitoring.services.temperature_sensors import TemperatureSensorsService
from app.v1.timestream.services.circuit_measurements_service import TimestreamElectricityCircuitMeasurementsService
from app.v1.timestream.services.electric_sensor_voltages_service import TimestreamElectricSensorVoltagesService
from app.v1.timestream.services.hvac_zone_measurements_service import TimestreamHvacZoneMeasurementsService
from app.v1.timestream.services.pes_averages_service import TimestreamPesAveragesService
from app.v1.timestream.services.temperature_sensor_place_measurements_service import TimestreamTemperatureSensorPlaceMeasurementsService
from app.v1.timestream.timestream_client import TimestreamClient
from app.v1.users.repositories.users_repository import PostgresUsersRepository
from app.v1.users.services.users import UsersService


load_dotenv()


JWT_ALGORITHM = os.environ.get('JWT_ALGORITHM', 'HS256')
JWT_ACCESS_TOKEN_SECRET_KEY = os.environ['JWT_ACCESS_TOKEN_SECRET_KEY']
JWT_REFRESH_TOKEN_SECRET_KEY = os.environ['JWT_REFRESH_TOKEN_SECRET_KEY']

DP_PES_URL = os.environ['DP_PES_URL']
DP_PES_API_KEY = os.environ['DP_PES_API_KEY']

TIMESTREAM_DATABASE_TEMPERATURE = os.environ["TIMESTREAM_DATABASE_TEMPERATURE"]
TIMESTREAM_TABLE_TEMPERATURE_PLACES = os.environ["TIMESTREAM_TABLE_TEMPERATURE_PLACES"]

TIMESTREAM_DATABASE_ELECTRICITY = os.environ["TIMESTREAM_DATABASE_ELECTRICITY"]
TIMESTREAM_TABLE_ELECTRICITY_CIRCUITS = os.environ["TIMESTREAM_TABLE_ELECTRICITY_CIRCUITS"]
TIMESTREAM_TABLE_PES_AVERAGES = os.environ["TIMESTREAM_TABLE_PES_AVERAGES"]

TIMESTREAM_DATABASE_HVAC = os.environ["TIMESTREAM_DATABASE_HVAC"]
TIMESTREAM_TABLE_CONTROL_ZONES = os.environ["TIMESTREAM_TABLE_CONTROL_ZONES"]

REDIS_CACHE_HOST = os.environ['REDIS_CACHE_HOST']
REDIS_CACHE_PORT = int(os.environ['REDIS_CACHE_PORT'])

LOGO_S3_BUCKET_NAME = os.environ['LOGO_S3_BUCKET_NAME']

logger = logging.getLogger()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/v1/auth/login",
    scopes={
        access_scope.value: description
        for access_scope, description in ACCESS_SCOPE_TO_DEFINITION.items()
    },
    auto_error=False
)

api_key_scheme = APIKeyHeader(
    name='X-POWERX-API-KEY',
    auto_error=False
)


# Access/Refresh token helpers
def get_refresh_token(
    request: Request,
) -> Optional[str]:
    authorization_header = request.headers.get('Authorization')
    if not authorization_header:
        return None
    scheme, _, param = authorization_header.partition(' ')
    if scheme.lower() != 'bearer':
        return None
    return param

def get_refresh_token_data(
    refresh_token: Optional[str] = Depends(get_refresh_token),
) -> RefreshTokenData:
    if refresh_token is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Missing token')
    try:
        decoded_refresh_token = jwt.decode(refresh_token, key=JWT_REFRESH_TOKEN_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token has expired')
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail='Invalid token')
    except Exception as e:
        logger.error(f'Error decoding refresh token: {e}')
        raise HTTPException(status_code=401, detail='Invalid token')
    refresh_token_data = RefreshTokenData(**decoded_refresh_token)
    return refresh_token_data

def get_access_token_data(
    token: Optional[str] = Depends(oauth2_scheme),
) -> Optional[AccessTokenData]:
    if token is None:
        return None
    try:
        decoded_token = jwt.decode(token, key=JWT_ACCESS_TOKEN_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidSignatureError:
        return None
    except Exception as e:
        logger.error(f'Error decoding access token: {e}')
        return None
    token_data = AccessTokenData(**decoded_token)
    return token_data


def get_access_token_data_or_raise(
    token_data: Optional[AccessTokenData] = Depends(get_access_token_data),
) -> AccessTokenData:
    if token_data is None:
        raise HTTPException(status_code=401, detail='Not Authenticated')
    return token_data

# Datastore clients
def get_db() -> Generator[Session, Any, None]:
    with SessionLocal() as db:
        yield db

def get_s3_client() -> S3Client:
    return boto3.client('s3')

def get_cache() -> Cache:
    return RedisCache(
        redis_host=REDIS_CACHE_HOST,
        redis_port=REDIS_CACHE_PORT,
        database_index=1
    )

def get_consumer_cache() -> Cache:
    return RedisCache(
        redis_host=REDIS_CACHE_HOST,
        redis_port=REDIS_CACHE_PORT,
        database_index=0
    )

def get_location_aggregated_data_cache() -> Cache:
    return RedisCache(
        redis_host=REDIS_CACHE_HOST,
        redis_port=REDIS_CACHE_PORT,
        database_index=2
    )


# Appliances module
def get_appliance_types_service(db_session: Session = Depends(get_db)) -> ApplianceTypesService:
    return ApplianceTypesService(
        appliance_types_repository=PostgresApplianceTypesRepository(db_session)
    )

def get_appliances_service(db_session: Session = Depends(get_db)) -> AppliancesService:
    return AppliancesService(
        appliances_repository=PostgresAppliancesRepository(db_session)
    )


# Auth module
def get_access_roles_service(db_session: Session = Depends(get_db)) -> AccessRolesService:
    return AccessRolesService(
        access_roles_repository=PostgresAccessRolesRepository(db_session)
    )

def get_access_role_access_scopes_service(db_session: Session = Depends(get_db)) -> AccessRoleAccessScopesService:
    return AccessRoleAccessScopesService(
        access_role_access_scopes_repository=PostgresAccessRoleAccessScopesRepository(db_session)
    )

def get_api_keys_service(db_session: Session = Depends(get_db)) -> APIKeysService:
    return APIKeysService(
        api_keys_repository=PostgresAPIKeysRepository(db_session)
    )

def get_api_key_access_scopes_service(db_session: Session = Depends(get_db)) -> APIKeyAccessScopesService:
    return APIKeyAccessScopesService(
        api_key_access_scopes_repository=PostgresAPIKeyAccessScopesRepository(db_session)
    )

def get_api_key_access_roles_service(db_session: Session = Depends(get_db)) -> APIKeyAccessRolesService:
    return APIKeyAccessRolesService(
        api_key_access_roles_repository=PostgresAPIKeyAccessRolesRepository(db_session)
    )

def get_api_key_data(
    api_key: Optional[str] = Security(api_key_scheme),
    api_keys_service: APIKeysService = Depends(get_api_keys_service)
) -> Optional[APIKey]:
    if api_key is None:
        return None
    return api_keys_service.get_api_key(api_key)

def get_user_access_roles_service(db_session: Session = Depends(get_db)) -> UserAccessRolesService:
    return UserAccessRolesService(
        user_access_roles_repository=PostgresUserAccessRolesRepository(db_session)
    )

def get_user_access_scopes_service(db_session: Session = Depends(get_db)) -> UserAccessScopesService:
    return UserAccessScopesService(
        user_access_scopes_repository=PostgresUserAccessScopesRepository(db_session)
    )

def get_user_location_access_grants_service(db_session: Session = Depends(get_db)) -> UserLocationAccessGrantsService:
    return UserLocationAccessGrantsService(
        user_location_access_grants_repository=PostgresUserLocationAccessGrantsRepository(db_session)    
    )

def get_user_organization_access_grants_service(db_session: Session = Depends(get_db)) -> UserOrganizationAccessGrantsService:
    return UserOrganizationAccessGrantsService(
        user_organization_access_grants_repository=PostgresUserOrganizationAccessGrantsRepository(db_session)    
    )


# Electricity Dashboards module
def get_electricity_dashboards_service(db_session: Session = Depends(get_db)) -> ElectricityDashboardsService:
    return ElectricityDashboardsService(
        electricity_dashboards_repository=PostgresElectricityDashboardsRepository(db_session)
    )

def get_energy_consumption_breakdown_electric_widgets_service(db_session: Session = Depends(get_db)) -> EnergyConsumptionBreakdownElectricWidgetsService:
    return EnergyConsumptionBreakdownElectricWidgetsService(
        repository=PostgresEnergyConsumptionBreakdownElectricWidgetRepository(db_session)
    )

def get_energy_load_curve_electric_widgets_service(db_session: Session = Depends(get_db)) -> EnergyLoadCurveElectricWidgetsService:
    return EnergyLoadCurveElectricWidgetsService(
        repository=PostgresEnergyLoadCurveElectricWidgetsRepository(db_session)
    )

def get_panel_system_health_electric_widgets_service(db_session: Session = Depends(get_db)) -> PanelSystemHealthElectricWidgetsService:
    return PanelSystemHealthElectricWidgetsService(
        repository=PostgresPanelSystemHealthElectricWidgetsRepository(db_session)
    )


# Electricity Monitoring module
def get_circuits_service(db_session: Session = Depends(get_db)) -> CircuitsService:
    return CircuitsService(
       circuits_repository=PostgresCircuitsRepository(db_session),
       electric_panels_repository=PostgresElectricPanelsRepository(db_session),
    )

def get_electric_panels_service(db_session: Session = Depends(get_db)) -> ElectricPanelsService:
    return ElectricPanelsService(
        electric_panels_repository=PostgresElectricPanelsRepository(db_session)
    )

def get_clamps_service(db_session: Session = Depends(get_db)) -> ClampsService:
    return ClampsService(
        clamps_repository=PostgresClampsRepository(db_session),
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session)
    )

def get_electric_sensors_service(db_session: Session = Depends(get_db)) -> ElectricSensorsService:
    return ElectricSensorsService(
        electric_sensors_repository=PostgresElectricSensorsRepository(db_session)
    )


# Hvac module
def get_hvac_zones_service(db_session: Session = Depends(get_db)) -> HvacZonesService:
    return HvacZonesService(
        hvac_zones_repository=PostgresHvacZonesRepository(db_session)
    )

def get_thermostats_service(db_session: Session = Depends(get_db)) -> ThermostatsService:
    return ThermostatsService(
        thermostats_repository=PostgresThermostatsRepository(db_session)
    )

def get_hvac_zone_temperature_sensors_service(db_session: Session = Depends(get_db)) -> HvacZoneTemperatureSensorsService:
    return HvacZoneTemperatureSensorsService(
        hvac_zone_temperature_sensors_repository=PostgresHvacZoneTemperatureSensorsRepository(db_session)
    )

def get_hvac_equipment_types_service(db_session: Session = Depends(get_db)) -> HvacEquipmentTypesService:
    return HvacEquipmentTypesService(
        hvac_equipment_types_repository=PostgresHvacEquipmentTypesRepository(db_session)
    )

def get_hvac_zone_equipment_service(db_session: Session = Depends(get_db)) -> HvacZoneEquipmentService:
    return HvacZoneEquipmentService(
        hvac_zone_equipment_repository=PostgresHvacZoneEquipmentRepository(db_session)
    )

def get_hvac_schedules_service(db_session: Session = Depends(get_db)) -> HvacSchedulesService:
    return HvacSchedulesService(
        hvac_schedules_repository=PostgresHvacSchedulesRepository(db_session),
        control_zone_hvac_widgets_repository=PostgresControlZoneHvacWidgetsRepository(db_session)
    )

def get_hvac_holds_service(db_session: Session = Depends(get_db)) -> HvacHoldsService:
    return HvacHoldsService(
        repository=PostgresHvacHoldsRepository(db_session)
    )


# Hvac Dashboards module
def get_hvac_dashboards_service(db_session: Session = Depends(get_db)) -> HvacDashboardsService:
    return HvacDashboardsService(
        hvac_dashboards_repository=PostgresHvacDashboardsRepository(db_session)
    )

def get_control_zone_hvac_widgets_service(
    db_session: Session = Depends(get_db),
    cache: Cache = Depends(get_cache),
    consumer_cache: Cache = Depends(get_consumer_cache)
) -> ControlZoneHvacWidgetsService:
    return ControlZoneHvacWidgetsService(
        control_zone_hvac_widgets_repository=PostgresControlZoneHvacWidgetsRepository(db_session),
        control_zone_temperature_place_links_repository=PostgresControlZoneTemperaturePlaceLinksRepository(db_session),
        cache=cache,
        consumer_cache=consumer_cache
    )


# Mesh Network module
def get_gateways_service(db_session: Session = Depends(get_db)) -> GatewaysService:
    return GatewaysService(
        gateways_repository=PostgresGatewaysRepository(db_session)
    )

def get_nodes_service(db_session: Session = Depends(get_db)) -> NodesService:
    return NodesService(
        nodes_repository=PostgresNodesRepository(db_session)
    )


# Organizations module
def get_organizations_service(db_session = Depends(get_db)) -> OrganizationsService:
    return OrganizationsService(
        organizations_repository=PostgresOrganizationsRepository(db_session)
    )

def get_organization_users_service(db_session: Session = Depends(get_db)) -> OrganizationUsersService:
    return OrganizationUsersService(
        organization_users_repository=PostgresOrganizationUsersRepository(db_session),
        organizations_repository=PostgresOrganizationsRepository(db_session)
    )

def get_organization_logos_service(
    db_session: Session = Depends(get_db),
    s3_client: S3Client = Depends(get_s3_client),
) -> OrganizationLogosService:
    return OrganizationLogosService(
        logo_s3_bucket_name=LOGO_S3_BUCKET_NAME,
        organizations_repository=PostgresOrganizationsRepository(db_session),
        s3_client=s3_client
    )

def get_organization_feature_toggles_service(db_session: Session = Depends(get_db)) -> OrganizationFeatureTogglesService:
    return OrganizationFeatureTogglesService(
        organization_feature_toggles_repository=PostgresOrganizationFeatureTogglesRepository(db_session)
    )


# Temperature Dashboards module
def get_temperature_dashboards_service(db_session: Session = Depends(get_db)) -> TemperatureDashboardsService:
    return TemperatureDashboardsService(
        temperature_dashboards_repository=PostgresTemperatureDashboardsRepository(db_session)
    )

def get_temperature_unit_widgets_service(db_session: Session = Depends(get_db)) -> TemperatureUnitWidgetsService:
    return TemperatureUnitWidgetsService(
        temperature_unit_widgets_repository=PostgresTemperatureUnitWidgetsRepository(db_session)
    )


# Temperature Monitoring module
def get_temperature_sensors_service(db_session: Session = Depends(get_db)) -> TemperatureSensorsService:
    return TemperatureSensorsService(
        temperature_sensors_repository=PostgresTemperatureSensorsRepository(db_session)
    )

def get_temperature_sensor_places_service(db_session: Session = Depends(get_db)) -> TemperatureSensorPlacesService:
    return TemperatureSensorPlacesService(
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session)
    )

def get_temperature_sensor_place_alerts_service(db_session: Session = Depends(get_db)) -> TemperatureSensorPlaceAlertsService:
    return TemperatureSensorPlaceAlertsService(
        temperature_sensor_place_alerts_repository=PostgresTemperatureSensorPlaceAlertsRepository(db_session),
        temperature_sensor_places_repository=PostgresTemperatureSensorPlacesRepository(db_session)
    )

def get_temperature_ranges_service(db_session: Session = Depends(get_db)) -> TemperatureRangesService:
    return TemperatureRangesService(
        temperature_ranges_repository=PostgresTemperatureRangesRepository(db_session)
    )

def get_temperature_sensor_place_readings_service(
    cache: Cache = Depends(get_cache)
) -> TemperatureSensorPlaceReadingsService:
    return TemperatureSensorPlaceReadingsService(
        temperature_sensor_place_readings_repository=CacheTemperatureSensorPlaceReadingsRepository(cache=cache)
    )


# Users module
def get_users_service(db_session: Session = Depends(get_db)) -> UsersService:
    return UsersService(
        users_repository=PostgresUsersRepository(db_session)
    )


# Locations module
def get_locations_service(db_session: Session = Depends(get_db)) -> LocationsService:
    return LocationsService(
        locations_repository=PostgresLocationsRepository(db_session)
    )

def get_location_electricity_prices_service(db_session: Session = Depends(get_db)) -> LocationElectricityPricesService:
    return LocationElectricityPricesService(
        location_electricity_prices_repository=PostgresLocationElectricityPricesRepository(db_session)
    )

def get_location_time_of_use_rates_service(db_session: Session = Depends(get_db)) -> LocationTimeOfUseRatesService:
    return LocationTimeOfUseRatesService(
        location_time_of_use_rates_repository=PostgresLocationTimeOfUseRatesRepository(db_session)
    )

def get_location_operating_hours_service(db_session: Session = Depends(get_db)) -> LocationOperatingHoursService:
    return LocationOperatingHoursService(
        location_operating_hours_repository=PostgresLocationOperatingHoursRepository(db_session)
    )


# Timestream services
def get_timestream_client() -> TimestreamClient:
    boto3_client = boto3.client('timestream-query')
    return TimestreamClient(
        query_client=boto3_client
    )

def get_timestream_temperature_sensor_place_measurements_service(timestream_client: TimestreamClient = Depends(get_timestream_client)) -> TimestreamTemperatureSensorPlaceMeasurementsService:
    return TimestreamTemperatureSensorPlaceMeasurementsService(
        database=TIMESTREAM_DATABASE_TEMPERATURE,
        table=TIMESTREAM_TABLE_TEMPERATURE_PLACES,
        client=timestream_client
    )

def get_timestream_electricity_circuit_measurements_service(timestream_client: TimestreamClient = Depends(get_timestream_client)) -> TimestreamElectricityCircuitMeasurementsService:
    return TimestreamElectricityCircuitMeasurementsService(
        database=TIMESTREAM_DATABASE_ELECTRICITY,
        table=TIMESTREAM_TABLE_ELECTRICITY_CIRCUITS,
        client=timestream_client
    )

def get_timestream_electric_sensor_voltages_service(timestream_client: TimestreamClient = Depends(get_timestream_client)) -> TimestreamElectricSensorVoltagesService:
    return TimestreamElectricSensorVoltagesService(
        database=TIMESTREAM_DATABASE_ELECTRICITY,
        table=TIMESTREAM_TABLE_PES_AVERAGES,
        client=timestream_client
    )

def get_timestream_hvac_zone_measurements_service(timestream_client: TimestreamClient = Depends(get_timestream_client)) -> TimestreamHvacZoneMeasurementsService:
    return TimestreamHvacZoneMeasurementsService(
        database=TIMESTREAM_DATABASE_HVAC,
        table=TIMESTREAM_TABLE_CONTROL_ZONES,
        client=timestream_client
    )

def get_timestream_pes_averages_service(time_stream_client: TimestreamClient = Depends(get_timestream_client)) -> TimestreamPesAveragesService:
    return TimestreamPesAveragesService(
        database=TIMESTREAM_DATABASE_ELECTRICITY,
        table=TIMESTREAM_TABLE_PES_AVERAGES,
        client=time_stream_client
    )


# Auth Helpers
def get_user_access_scopes_helper(
    user_access_scopes_service: UserAccessScopesService = Depends(get_user_access_scopes_service),
    user_access_roles_service: UserAccessRolesService = Depends(get_user_access_roles_service),
    access_role_access_scopes_service: AccessRoleAccessScopesService = Depends(get_access_role_access_scopes_service)
) -> UserAccessScopesHelper:
    return UserAccessScopesHelper(
        user_access_scopes_service=user_access_scopes_service,
        user_access_roles_service=user_access_roles_service,
        access_role_access_scopes_service=access_role_access_scopes_service
    )

def get_user_access_grants_helper(
    user_organization_access_grants_service: UserOrganizationAccessGrantsService = Depends(get_user_organization_access_grants_service),
    user_location_access_grants_service: UserLocationAccessGrantsService = Depends(get_user_location_access_grants_service)
) -> UserAccessGrantsHelper:
    return UserAccessGrantsHelper(
        user_organization_access_grants_service=user_organization_access_grants_service,
        user_location_access_grants_service=user_location_access_grants_service
    )

def get_api_key_access_scopes_helper(
    api_key_access_scopes_service: APIKeyAccessScopesService = Depends(get_api_key_access_scopes_service),
    api_key_access_roles_service: APIKeyAccessRolesService = Depends(get_api_key_access_roles_service),
    access_role_access_scopes_service: AccessRoleAccessScopesService = Depends(get_access_role_access_scopes_service)
) -> APIKeyAccessScopesHelper:
    return APIKeyAccessScopesHelper(
        api_key_access_scopes_service=api_key_access_scopes_service,
        api_key_access_roles_service=api_key_access_roles_service,
        access_role_access_scopes_service=access_role_access_scopes_service
    )

def verify_any_authorization(
    security_scopes: SecurityScopes,
    api_key: Optional[APIKey] = Depends(get_api_key_data),
    access_token: Optional[AccessTokenData] = Depends(get_access_token_data),
    api_keys_access_scopes_helper: APIKeyAccessScopesHelper = Depends(get_api_key_access_scopes_helper),
) -> None:
    if not api_key and not access_token:
        raise HTTPException(status_code=401, detail="Not Authenticated")
    
    if api_key:
        if security_scopes is None or len(security_scopes.scopes) == 0:
            return
        api_key_scopes: List[AccessScope] = api_keys_access_scopes_helper.get_all_access_scopes_for_api_key(api_key.api_key_id)
        for scope in security_scopes.scopes:
            if scope not in api_key_scopes:
                raise HTTPException(status_code=403, detail="Not Authorized")
    
    if access_token:
        if security_scopes is None or len(security_scopes.scopes) == 0:
            return
        for scope in security_scopes.scopes:
            if scope not in access_token.access_scopes:
                raise HTTPException(status_code=403, detail="Not Authorized")

def verify_jwt_authorization(
    security_scopes: SecurityScopes,
    access_token: Optional[AccessTokenData] = Depends(get_access_token_data)
) -> None:
    if access_token is None:
        raise HTTPException(status_code=401, detail="Not Authenticated")
    
    if security_scopes is None or len(security_scopes.scopes) == 0:
        return
    
    for scope in security_scopes.scopes:
        if scope not in access_token.access_scopes:
            raise HTTPException(status_code=403, detail="Not Authorized")

def verify_api_key_authorization(
    security_scopes: SecurityScopes,
    api_key: Optional[APIKey] = Depends(get_api_key_data),
    api_keys_access_scopes_helper: APIKeyAccessScopesHelper = Depends(get_api_key_access_scopes_helper)
) -> None:
    if api_key is None:
        raise HTTPException(status_code=401, detail="Not Authenticated")
    
    if security_scopes is None or len(security_scopes.scopes) == 0:
        return
    
    api_key_scopes: List[AccessScope] = api_keys_access_scopes_helper.get_all_access_scopes_for_api_key(api_key.api_key_id)
    for scope in security_scopes.scopes:
        if scope not in api_key_scopes:
            raise HTTPException(status_code=403, detail="Not Authorized")


# DP PES module
def get_dp_pes_client() -> DpPesClient:
    return DpPesClient(
        url=DP_PES_URL,
        apikey=DP_PES_API_KEY
    )

def get_dp_pes_service(
    dp_pes_client: DpPesClient = Depends(get_dp_pes_client),
    thermostats_service: ThermostatsService = Depends(get_thermostats_service),
    hvac_zones_service: HvacZonesService = Depends(get_hvac_zones_service),
    hvac_schedules_service: HvacSchedulesService = Depends(get_hvac_schedules_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    gateways_service: GatewaysService = Depends(get_gateways_service),
    nodes_service: NodesService = Depends(get_nodes_service),
    organizations_service: OrganizationsService = Depends(get_organizations_service),
    organization_feature_toggles_service: OrganizationFeatureTogglesService = Depends(get_organization_feature_toggles_service),
    locations_service: LocationsService = Depends(get_locations_service),
    control_zone_hvac_widgets_service: ControlZoneHvacWidgetsService = Depends(get_control_zone_hvac_widgets_service),
    hvac_holds_service: HvacHoldsService = Depends(get_hvac_holds_service),
    electric_sensors_service: ElectricSensorsService = Depends(get_electric_sensors_service),
    location_electricity_prices_service: LocationElectricityPricesService = Depends(get_location_electricity_prices_service),
    location_time_of_use_rates_service: LocationTimeOfUseRatesService = Depends(get_location_time_of_use_rates_service),
    clamps_service: ClampsService = Depends(get_clamps_service),
    circuits_service: CircuitsService = Depends(get_circuits_service),
) -> DpPesService:
    return DpPesService(
        dp_pes_client=dp_pes_client,
        thermostats_service=thermostats_service,
        hvac_zones_service=hvac_zones_service,
        hvac_schedules_service=hvac_schedules_service,
        hvac_dashboards_service=hvac_dashboards_service,
        gateways_service=gateways_service,
        nodes_service=nodes_service,
        organizations_service=organizations_service,
        organization_feature_toggles_service=organization_feature_toggles_service,
        locations_service=locations_service,
        control_zone_hvac_widgets_service=control_zone_hvac_widgets_service,
        hvac_holds_service=hvac_holds_service,
        electric_sensors_service=electric_sensors_service,
        location_electricity_prices_service=location_electricity_prices_service,
        location_time_of_use_rates_service=location_time_of_use_rates_service,
        clamps_service=clamps_service,
        circuits_service=circuits_service
    )


# Device Status module
def get_location_devices_repository(db_session: Session = Depends(get_db)) -> LocationDevicesRepository:
    return PostgresLocationDevicesRepository(db_session)


def get_device_status_service(
    cache: Cache = Depends(get_cache),
    location_devices_repository: LocationDevicesRepository = Depends(get_location_devices_repository),
) -> DeviceStatusService:
    return DeviceStatusService(
        cache=cache,
        location_devices_repository=location_devices_repository,
    )
