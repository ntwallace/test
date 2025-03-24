from datetime import datetime
from itertools import chain, groupby
import logging
from typing import Dict, List, Optional
from uuid import uuid4, UUID
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, Header, Path, Query, UploadFile, status


from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.auth.schemas.all_location_role import AllLocationRole
from app.v1.auth.schemas.organization_access_grant import OrganizationAccessGrant
from app.v1.auth.schemas.organization_role import OrganizationRole
from app.v1.auth.schemas.per_location_role import PerLocationRole
from app.v1.auth.services.user_location_access_grants import UserLocationAccessGrantsService
from app.v1.auth.services.user_organization_access_grants import UserOrganizationAccessGrantsService
from app.v1.dependencies import (
    get_access_token_data,
    get_electricity_dashboards_service,
    get_hvac_dashboards_service,
    get_organization_logos_service,
    get_organization_users_service,
    get_locations_service,
    get_organization_feature_toggles_service,
    get_organizations_service,
    get_temperature_dashboards_service,
    get_temperature_sensor_place_alerts_service,
    get_temperature_sensor_places_service,
    get_temperature_unit_widgets_service,
    get_user_location_access_grants_service,
    get_user_organization_access_grants_service,
    get_user_access_grants_helper,
    get_users_service,
    get_temperature_sensor_place_readings_service
)
from app.v1.electricity_dashboards.services.electricity_dashboards_service import ElectricityDashboardsService
from app.v1.hvac_dashboards.services.hvac_dashboards_service import HvacDashboardsService
from app.v1.locations.schemas.location import Location
from app.v1.locations.services.locations import LocationsService
from app.v1.organizations.schemas.organization import Organization
from app.v1.organizations.schemas.organization_feature_toggle import OrganizationFeatureToggle
from app.v1.organizations.schemas.organization_user import OrganizationUserCreate
from app.v1.organizations.services.organization_feature_toggles import OrganizationFeatureTogglesService
from app.v1.organizations.services.organization_logos import OrganizationLogosService
from app.v1.organizations.services.organization_users import OrganizationUsersService
from app.v1.organizations.services.organizations import OrganizationsService
from app.v1.schemas import AccessTokenData
from app.v1.temperature_monitoring.schemas.temperature_sensor_place import TemperatureSensorPlace
from app.v1.temperature_monitoring.schemas.temperature_sensor_place_alert import TemperatureSensorPlaceAlert
from app.v1.temperature_monitoring.schemas.temperature_sensor_place_reading import TemperatureSensorPlaceReading
from app.v1.temperature_monitoring.services.temperature_sensor_place_alerts import TemperatureSensorPlaceAlertsService
from app.v1.temperature_monitoring.services.temperature_sensor_place_readings import TemperatureSensorPlaceReadingsService
from app.v1.temperature_monitoring.services.temperature_sensor_places import TemperatureSensorPlacesService
from app.v1.users.schemas.user import UserCreate
from app.v1.users.services.users import UsersService
from app.v1.utils import convert_to_utc
from app.v3_adapter.organizations.schemas import (
    GetOrganizationAlertsResponse,
    GetOrganizationAlertsResponseDataItem,
    GetOrganizationAlertsResponseDataItemLocation,
    GetOrganizationAlertsResponseDataItemTarget,
    GetOrganizationLocationsResponse,
    GetOrganizationLocationsResponseDataItem,
    GetOrganizationsResponse,
    DeleteOrganizationAccountResponse,
    GetOrganizationAccountsResponse,
    GetOrganizationAccountsResponseDataItem,
    GetOrganizationResponse,
    GetOrganizationResponseData,
    GetOrganizationResponseDataLocation,
    GetOrganizationRolesResponse,
    GetOrganizationRolesResponseData,
    GetOrganizationsResponseDataItem,
    PerLocationRoleItem,
    PostOrganizationAccountsRequestBody,
    PostOrganizationAccountsResponse,
    PostOrganizationAccountsResponseData,
    PutOrganizationLogoResponse,
    PutOrganizationRoleRequestBody,
    PutOrganizationRoleResponse,
    PutOrganizationRoleResponseData
)
from app.v1.temperature_dashboards.schemas.temperature_dashboard import TemperatureDashboard
from app.v1.temperature_dashboards.services.temperature_dashboards_service import TemperatureDashboardsService
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import TemperatureUnitWidget
from app.v1.temperature_dashboards.services.temperature_unit_widgets_service import TemperatureUnitWidgetsService

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_MAX_FILE_SIZE = 1024 * 1024 * 5  # 5MB


router = APIRouter()


def _get_organization(
    organization_id: UUID = Path(alias='id'),
    organizations_service: OrganizationsService = Depends(get_organizations_service)
) -> Organization:
    organization = organizations_service.get_organization_by_organization_id(organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Organization not found')
    return organization


def _authorize_token_for_organization_read(
    organization: Organization = Depends(_get_organization),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if not user_access_grants_helper.is_user_authorized_for_organization_read(access_token_data.user_id, organization.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to read organization')

def _authorize_token_for_organization_update(
    organization: Organization = Depends(_get_organization),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if not user_access_grants_helper.is_user_authorized_for_organization_update(access_token_data.user_id, organization.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to update organization')


@router.get(
    '/organizations',
    dependencies=[Depends(get_access_token_data)],
    response_model=GetOrganizationsResponse
)
def get_organizations(
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    organizations_service: OrganizationsService = Depends(get_organizations_service),
    user_organization_access_grants_service: UserOrganizationAccessGrantsService = Depends(get_user_organization_access_grants_service),
):
    user_organization_access_grants = user_organization_access_grants_service.get_user_organization_access_grants(access_token_data.user_id)
    read_access_organization_ids = [
        user_organization_access_grant.organization_id
        for user_organization_access_grant in user_organization_access_grants
        if user_organization_access_grant.organization_access_grant == OrganizationAccessGrant.ALLOW_READ_ORGANIZATION
    ]
    organizations = organizations_service.get_organizations_by_organization_ids(read_access_organization_ids)
    return GetOrganizationsResponse(
        code='200',
        message='Success',
        data=[
            GetOrganizationsResponseDataItem(
                id=organization.organization_id,
                name=organization.name
            )
            for organization in organizations
        ]
    )
    

@router.get(
    '/organizations/{id}',
    dependencies=[Depends(_authorize_token_for_organization_read)],
    response_model=GetOrganizationResponse
)
def get_organization(
    organization: Organization = Depends(_get_organization),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    organization_users_service: OrganizationUsersService = Depends(get_organization_users_service),
    organization_feature_toggles_service: OrganizationFeatureTogglesService = Depends(get_organization_feature_toggles_service),
    organization_logos_service: OrganizationLogosService = Depends(get_organization_logos_service),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    locations = locations_service.get_locations_by_organization_id(organization.organization_id)
    organization_owner = organization_users_service.get_organization_owner(organization.organization_id)
    if organization_owner is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Organization owner not found')
    
    organization_feature_toggles: List[OrganizationFeatureToggle] = organization_feature_toggles_service.get_feature_toggles_for_organization(organization.organization_id)

    location_dashboards: Dict[UUID, List[Dict]] = {}
    for location in locations:
        if location.location_id not in location_dashboards:
            location_dashboards[location.location_id] = []
        location_dashboards[location.location_id].extend([
            {
                'id': electricity_dashboard.electricity_dashboard_id,
                'name': electricity_dashboard.name,
                'dashboard_type': 'Electricity'
            }
            for electricity_dashboard in electricity_dashboards_service.filter_by(location_id=location.location_id)
        ])
        location_dashboards[location.location_id].extend([
            {
                'id': temperature_dashboard.temperature_dashboard_id,
                'name': temperature_dashboard.name,
                'dashboard_type': 'Temperature'
            }
            for temperature_dashboard in temperature_dashboards_service.get_temperature_dashboards_for_location(location.location_id)
        ])
        location_dashboards[location.location_id].extend([
            {
                'id': hvac_dashboard.hvac_dashboard_id,
                'name': hvac_dashboard.name,
                'dashboard_type': 'Hvac'
            }
            for hvac_dashboard in hvac_dashboards_service.get_hvac_dashboards_for_location(location.location_id)
        ])
    
    logo_url: Optional[str] = organization_logos_service.get_logo_url(organization.organization_id)

    return GetOrganizationResponse(
        code='200',
        message='Success',
        data=GetOrganizationResponseData(
            id=organization.organization_id,
            name=organization.name,
            owner_id=organization_owner.user_id,
            toggles=[
                organization_feature_toggle.organization_feature_toggle.value
                for organization_feature_toggle in organization_feature_toggles
            ],
            logo_url=logo_url,
            locations=[
                GetOrganizationResponseDataLocation(
                    id=location.location_id,
                    name=location.name,
                    address=location.address,
                    timezone=location.timezone,
                    state=location.state,
                    city=location.city,
                    dashboards=location_dashboards.get(location.location_id, [])
                )
                for location in locations
                if user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location)
            ]
        )
    )


@router.get(
    '/organizations/{id}/locations',
    dependencies=[Depends(_authorize_token_for_organization_read)],
    response_model=GetOrganizationLocationsResponse
)
def get_organization_locations(
    organization: Organization = Depends(_get_organization),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    locations_service: LocationsService = Depends(get_locations_service),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    locations = locations_service.get_locations_by_organization_id(organization.organization_id)
    return GetOrganizationLocationsResponse(
        code='200',
        message='Success',
        data=[
            GetOrganizationLocationsResponseDataItem(
                id=location.location_id,
                name=location.name,
                address=location.address,
                timezone=location.timezone
            )
            for location in locations
            if user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location)
        ]
    )
    

@router.put(
    '/organizations/{id}/logo',
    dependencies=[Depends(_authorize_token_for_organization_update)],
    response_model=PutOrganizationLogoResponse
)
async def put_organization_logo(
    logo_file: UploadFile,
    content_length: int = Header(lt=_MAX_FILE_SIZE),
    organization: Organization = Depends(_get_organization),
    organization_logos_service: OrganizationLogosService = Depends(get_organization_logos_service)
):
    try:
        await organization_logos_service.update_organization_logo(organization.organization_id, logo_file)
    except ValueError as e:
        logger.error(f"ValueError while trying to update logo: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Exception while uploading logo: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Error uploading logo')
    
    return PutOrganizationLogoResponse(
        code='201',
        message='Success',
        data=None
    )

@router.post(
    '/organizations/{id}/accounts',
    dependencies=[Depends(_authorize_token_for_organization_update)],
    response_model=PostOrganizationAccountsResponse
)
def post_organization_accounts(
    post_organization_accounts_request: PostOrganizationAccountsRequestBody,
    organization: Organization = Depends(_get_organization),
    organization_users_service: OrganizationUsersService = Depends(get_organization_users_service),
    users_service: UsersService = Depends(get_users_service),
):
    new_organizatin_user = users_service.get_user_by_email(post_organization_accounts_request.email)
    if new_organizatin_user is None:
        new_organizatin_user = users_service.create_user(
            UserCreate(
                first_name=post_organization_accounts_request.given_name,
                last_name=post_organization_accounts_request.family_name,
                email=post_organization_accounts_request.email,
                password=None
            )
        )
    organization_users_service.create_organization_user(
        OrganizationUserCreate(
            organization_id=organization.organization_id,
            user_id=new_organizatin_user.user_id,
            is_organization_owner=False
        )
    )
    return PostOrganizationAccountsResponse(
        code='200',
        message='Success',
        data=PostOrganizationAccountsResponseData(
            id=new_organizatin_user.user_id,
            given_name=new_organizatin_user.first_name,
            family_name=new_organizatin_user.last_name,
            email=new_organizatin_user.email
        )
    )

@router.get(
    '/organizations/{id}/accounts',
    dependencies=[Depends(_authorize_token_for_organization_read)],
    response_model=GetOrganizationAccountsResponse
)
def get_organization_accounts(
    organization: Organization = Depends(_get_organization),
    locations_service: LocationsService = Depends(get_locations_service),
    organization_users_service: OrganizationUsersService = Depends(get_organization_users_service),
    users_service: UsersService = Depends(get_users_service),
    user_organization_access_grants_service: UserOrganizationAccessGrantsService = Depends(get_user_organization_access_grants_service),
    user_location_access_grants_service: UserLocationAccessGrantsService = Depends(get_user_location_access_grants_service)
):
    locations = locations_service.get_locations_by_organization_id(organization.organization_id)
    location_map = {
        location.location_id: location
        for location in locations
    }

    organization_users = organization_users_service.get_organization_users(organization.organization_id)
    organization_user_map = {
        organization_user.user_id: organization_user
        for organization_user in organization_users
    }

    users = users_service.get_users_by_ids([organization_user.user_id for organization_user in organization_users])

    user_organization_access_roles_map: Dict[UUID, List[OrganizationRole]] = {}
    user_all_location_access_roles_map: Dict[UUID, List[AllLocationRole]] = {}
    user_per_location_access_roles_map: Dict[UUID, Dict[UUID, List[PerLocationRole]]] = {}
    for user in users:
        user_organization_access_roles_map[user.user_id] = []
        user_all_location_access_roles_map[user.user_id] = []
        user_per_location_access_roles_map[user.user_id] = {}

        user_organization_access_grants = set([
            user_organization_access_grant.organization_access_grant
            for user_organization_access_grant in user_organization_access_grants_service.get_user_organization_access_grants(user.user_id)
            if user_organization_access_grant.organization_id == organization.organization_id
        ])
        for organization_role in OrganizationRole:
            organization_role_access_grants = set(organization_role.get_organization_access_grants())
            if user_organization_access_grants.intersection(OrganizationAccessGrant.get_organization_access_grants()) == organization_role_access_grants:
                user_organization_access_roles_map[user.user_id].append(organization_role)
        
        for all_location_role in AllLocationRole:
            all_location_role_access_grants = set(all_location_role.get_organization_access_grants())
            if user_organization_access_grants.intersection(OrganizationAccessGrant.get_all_location_access_grants()) == all_location_role_access_grants:
                user_all_location_access_roles_map[user.user_id].append(all_location_role)
        
        user_location_access_grants = user_location_access_grants_service.get_user_location_access_grants(user.user_id)
        for (location_id, location_access_grants) in groupby(user_location_access_grants, key=lambda location_access_grant: location_access_grant.location_id):
            user_per_location_access_roles_map[user.user_id][location_id] = []
            user_location_access_grants_for_location = set([
                user_location_access_grant.location_access_grant
                for user_location_access_grant in location_access_grants
            ])
            for per_location_role in PerLocationRole:
                per_location_role_access_grants = set(per_location_role.get_location_access_grants())
                if user_location_access_grants_for_location == per_location_role_access_grants:
                    user_per_location_access_roles_map[user.user_id][location_id].append(per_location_role)

    return GetOrganizationAccountsResponse(
        code='200',
        message='Success',
        data=[
            GetOrganizationAccountsResponseDataItem(
                id=user.user_id,
                email=user.email,
                given_name=user.first_name,
                family_name=user.last_name,
                owner=organization_user_map[user.user_id].is_organization_owner,
                organization_roles=user_organization_access_roles_map[user.user_id],
                all_location_roles=user_all_location_access_roles_map[user.user_id],
                per_location_roles=[
                    PerLocationRoleItem(
                        location_id=location_id,
                        location_name=location_map[location_id].name,
                        roles=user_per_location_access_roles,
                        name=location_map[location_id].name,
                        address=location_map[location_id].address
                    )
                    for location_id, user_per_location_access_roles in user_per_location_access_roles_map[user.user_id].items()
                    if location_id in location_map
                ],
            )
            for user in users
        ]
    )

@router.delete(
    '/organizations/{id}/accounts',
    dependencies=[Depends(_authorize_token_for_organization_update)],
    response_model=DeleteOrganizationAccountResponse
)
def delete_organization_account(
    user_id: UUID = Query(alias='account_id'),
    organization: Organization = Depends(_get_organization),
    locations_service: LocationsService = Depends(get_locations_service),
    organization_users_service: OrganizationUsersService = Depends(get_organization_users_service),
    user_organization_access_grants_service: UserOrganizationAccessGrantsService = Depends(get_user_organization_access_grants_service),
    user_location_access_grants_service: UserLocationAccessGrantsService = Depends(get_user_location_access_grants_service)
):
    locations = locations_service.get_locations_by_organization_id(organization.organization_id)

    organization_users_service.delete_organization_user(organization.organization_id, user_id)
    user_organization_access_grants_service.remove_user_organization_access_grants(user_id, organization.organization_id)

    for location in locations:
        user_location_access_grants_service.remove_user_location_access_grants(user_id, location.location_id)

    return DeleteOrganizationAccountResponse(
        code='200',
        message='Success',
        data=user_id
    )


@router.put(
    '/organizations/{id}/roles',
    dependencies=[Depends(_authorize_token_for_organization_update)],
    response_model=PutOrganizationRoleResponse
)
def put_organization_role(
    organization_role_request: PutOrganizationRoleRequestBody,
    user_id: UUID = Query(alias='account_id'),
    organization: Organization = Depends(_get_organization),
    user_organization_access_grants_service: UserOrganizationAccessGrantsService = Depends(get_user_organization_access_grants_service),
):
    organization_access_grants = set([
        organization_access_grant
        for organization_role in organization_role_request.organization_roles
        for organization_access_grant in organization_role.get_organization_access_grants()
    ])
    all_location_access_grants = set([
        location_access_grant
        for all_location_role in organization_role_request.all_location_roles
        for location_access_grant in all_location_role.get_organization_access_grants()
    ])
    access_grants = list(chain(organization_access_grants, all_location_access_grants))
    user_organization_access_grants_service.set_user_organization_access_grants(user_id, organization.organization_id, access_grants)

    return PutOrganizationRoleResponse(
        code='200',
        message='Success',
        data=PutOrganizationRoleResponseData(
            id=uuid4(),  # TODO: Check if this is ok, permission object doesn't exist in this schema
            organization=organization.organization_id,
            account=user_id
        )
    )

@router.get(
    '/organizations/{id}/roles',
    dependencies=[Depends(_authorize_token_for_organization_read)],
    response_model=GetOrganizationRolesResponse
)
def get_organization_roles(
    organization_id: UUID = Path(alias='id'),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    user_organization_access_grants_service: UserOrganizationAccessGrantsService = Depends(get_user_organization_access_grants_service),
):
    user_organization_access_grants = set([
        user_organization_access_grant.organization_access_grant
        for user_organization_access_grant in user_organization_access_grants_service.get_user_organization_access_grants(access_token_data.user_id)
        if user_organization_access_grant.organization_id == organization_id
    ]).intersection(OrganizationAccessGrant.get_organization_access_grants())
    
    roles: List[OrganizationRole] = []
    for role in OrganizationRole:
        organization_role_access_grants = set(role.get_organization_access_grants())
        if user_organization_access_grants == organization_role_access_grants:
            roles.append(role)
    
    return GetOrganizationRolesResponse(
        code='200',
        message='Success',
        data=GetOrganizationRolesResponseData(
            organization_roles=roles
        )
    )


@router.get(
    '/organizations/{id}/alerts',
    dependencies=[Depends(_authorize_token_for_organization_read)],
    response_model=GetOrganizationAlertsResponse
)
def get_organization_alerts(
    period_start: datetime,
    period_end: datetime,
    organization: Organization = Depends(_get_organization),
    locations_service: LocationsService = Depends(get_locations_service),
    temperature_sensor_places_service: TemperatureSensorPlacesService = Depends(get_temperature_sensor_places_service),
    temperature_sensor_place_alerts_service: TemperatureSensorPlaceAlertsService = Depends(get_temperature_sensor_place_alerts_service),
    temperature_sensor_place_readings_service: TemperatureSensorPlaceReadingsService = Depends(get_temperature_sensor_place_readings_service),
    temperature_unit_widgets_service: TemperatureUnitWidgetsService = Depends(get_temperature_unit_widgets_service),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service)
):
    period_start = convert_to_utc(period_start)
    period_end = convert_to_utc(period_end)

    locations = locations_service.get_locations_by_organization_id(organization.organization_id)
    locations_map: Dict[UUID, Location] = {
        location.location_id: location
        for location in locations
    }

    temperature_dashboards: List[TemperatureDashboard] = []
    for location in locations:
        temperature_dashboards.extend(
            temperature_dashboards_service.get_temperature_dashboards_for_location(location.location_id)
        )
    location_id_to_temperature_dashboard_map: Dict[UUID, TemperatureDashboard] = {
        temperature_dashboard.location_id: temperature_dashboard
        for temperature_dashboard in temperature_dashboards
    }

    temperature_unit_widgets: List[TemperatureUnitWidget] = []
    for temperature_dashboard in temperature_dashboards:
        temperature_unit_widgets.extend(
            temperature_unit_widgets_service.get_temperature_unit_widgets_for_temperature_dashboard(temperature_dashboard.temperature_dashboard_id)
        )
    temperature_unit_widgets_map: Dict[UUID, TemperatureUnitWidget] = {
        temperature_unit_widget.temperature_sensor_place_id: temperature_unit_widget
        for temperature_unit_widget in temperature_unit_widgets
    }

    temperature_sensor_places: List[TemperatureSensorPlace] = []
    temperature_sensor_place_alerts: List[TemperatureSensorPlaceAlert] = []
    for location in locations:
        temperature_sensor_places.extend(
            temperature_sensor_places_service.get_temperature_sensor_places_for_location(location.location_id)
        )
        temperature_sensor_place_alerts.extend(
            temperature_sensor_place_alerts_service.get_temperature_sensor_place_alerts_for_location(
                location.location_id,
                period_start,
                period_end,
                tz_string=location.timezone
            )
        )
    
    temperature_sensor_places_map: Dict[UUID, TemperatureSensorPlace] = {
        temperature_sensor_place.temperature_sensor_place_id: temperature_sensor_place
        for temperature_sensor_place in temperature_sensor_places
    }

    current_temperature_place_temps: Dict[UUID, Optional[TemperatureSensorPlaceReading]] = {}
    for temperature_sensor_place in temperature_sensor_places:
        current_temperature_place_temps[temperature_sensor_place.temperature_sensor_place_id] = temperature_sensor_place_readings_service.get_latest_activity_for_temperature_sensor_place(temperature_sensor_place.temperature_sensor_place_id)
    
    response_data_items: List[GetOrganizationAlertsResponseDataItem] = []
    for alert in temperature_sensor_place_alerts:
        temperature_sensor_place = temperature_sensor_places_map[alert.temperature_sensor_place_id]
        temperature_unit_widget = temperature_unit_widgets_map[alert.temperature_sensor_place_id]
        location = locations_map[temperature_sensor_place.location_id]
        temperature_dashboard = location_id_to_temperature_dashboard_map[location.location_id]
        current_temp = getattr(current_temperature_place_temps[alert.temperature_sensor_place_id], 'temperature_c', None)
        response_data_items.append(
            GetOrganizationAlertsResponseDataItem(
                id=alert.temperature_sensor_place_alert_id,
                location=GetOrganizationAlertsResponseDataItemLocation(
                    id=location.location_id,
                    name=location.name,
                    timezone=location.timezone
                ),
                started=alert.started_at.astimezone(tz=ZoneInfo(location.timezone)),
                resolved=alert.ended_at.astimezone(tz=ZoneInfo(location.timezone)) if alert.ended_at else None,
                threshold_c=alert.threshold_temperature_c,
                threshold_type=alert.alert_type.to_api_response_string(),
                threshold_window_s=alert.threshold_window_seconds,
                current_temperature_c=current_temp,
                target=GetOrganizationAlertsResponseDataItemTarget(
                    id=temperature_sensor_place.temperature_sensor_place_id,
                    temperature_place_id=temperature_sensor_place.temperature_sensor_place_id,
                    temperature_dashboard_id=temperature_dashboard.temperature_dashboard_id,
                    name=temperature_unit_widget.name
                ),
            )
        )

    return GetOrganizationAlertsResponse(
        code='200',
        message='Success',
        data=response_data_items
    )
    