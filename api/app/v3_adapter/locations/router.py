from datetime import datetime, timedelta, timezone
from decimal import Decimal
from itertools import chain
from typing import List, Optional, Tuple
from uuid import uuid4, UUID
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Depends, HTTPException, Path, status

from app.v1.auth.helpers.user_access_grants_helper import UserAccessGrantsHelper
from app.v1.auth.schemas.all_location_role import AllLocationRole
from app.v1.auth.schemas.organization_access_grant import OrganizationAccessGrant
from app.v1.auth.schemas.per_location_role import PerLocationRole
from app.v1.auth.services.user_location_access_grants import UserLocationAccessGrantsService
from app.v1.auth.services.user_organization_access_grants import UserOrganizationAccessGrantsService
from app.v1.cache.cache import Cache
from app.v1.dependencies import (
    get_access_token_data,
    get_dp_pes_service,
    get_electricity_dashboards_service,
    get_hvac_dashboards_service,
    get_location_aggregated_data_cache,
    get_location_electricity_prices_service,
    get_location_time_of_use_rates_service,
    get_circuits_service,
    get_location_operating_hours_service,
    get_locations_service,
    get_temperature_dashboards_service,
    get_temperature_sensor_place_alerts_service,
    get_user_location_access_grants_service,
    get_user_organization_access_grants_service,
    get_timestream_electricity_circuit_measurements_service,
    get_user_access_grants_helper
)
from app.v1.dp_pes.service import DpPesService
from app.v1.electricity_dashboards.services.electricity_dashboards_service import ElectricityDashboardsService
from app.v1.electricity_monitoring.schemas.circuit import CircuitTypeEnum
from app.v1.electricity_monitoring.services.circuits import CircuitsService
from app.v1.hvac_dashboards.services.hvac_dashboards_service import HvacDashboardsService
from app.v1.locations.schemas.location import Location
from app.v1.locations.schemas.location_electricity_price import LocationElectricityPriceCreate
from app.v1.locations.schemas.location_operating_hours import LocationOperatingHoursUpdate
from app.v1.locations.schemas.location_time_of_use_rate import LocationTimeOfUseRateCreate, LocationTimeOfUseRateUpdate
from app.v1.locations.services.location_electricity_prices import LocationElectricityPricesService
from app.v1.locations.services.location_operating_hours import LocationOperatingHoursService
from app.v1.locations.services.location_time_of_use_rates import LocationTimeOfUseRatesService
from app.v1.locations.services.locations import LocationsService
from app.v1.schemas import AccessTokenData, DayOfWeek
from app.v1.temperature_monitoring.services.temperature_sensor_place_alerts import TemperatureSensorPlaceAlertsService
from app.v1.timestream.services.circuit_measurements_service import TimestreamElectricityCircuitMeasurementsService
from app.v3_adapter.locations.schemas import (
    DeleteLocationRolesResponse,
    ExtendedOperatingHours,
    GetLocationAlertsResponse,
    GetLocationAlertsResponseData,
    GetLocationDashboardsResponse,
    GetLocationElectricityUsageMtdResponse,
    GetLocationElectricityUsageMtdResponseData,
    GetLocationEnergyUsageTrendResponse,
    GetLocationEnergyUsageTrendResponseData,
    GetLocationOperatingHoursResponse,
    GetLocationOperatingHoursResponseData,
    GetLocationResponse,
    GetLocationResponseData,
    GetLocationRolesResponse,
    GetLocationRolesResponseData,
    GetLocationTimeOfUseRateResponseDataItem,
    GetLocationTimeOfUseRatesResponse,
    GetLocationUsageChangeResponse,
    GetLocationUsageChangeResponseData,
    LocationDashboardType,
    LocationDashboardsResponseDataItem,
    OperatingHours,
    PatchLocationTimeOfUseRateRequestBody,
    PatchLocationTimeOfUseRateResponse,
    PatchLocationTimeOfUseRateResponseData,
    PostLocationElectricityPriceRequestBody,
    PostLocationElectricityPriceResponse,
    PostLocationElectricityPriceResponseData,
    PostLocationTimeOfUseRateRequestBody,
    PostLocationTimeOfUseRateResponse,
    PostLocationTimeOfUseRateResponseData,
    PulocationOperatingHoursResponseData,
    PutLocationOperatingHoursExtendedRequestBody,
    PutLocationOperatingHoursExtendedResponse,
    PutLocationOperatingHoursExtendedResponseData,
    PutLocationOperatingHoursRequestBody,
    PutLocationOperatingHoursResponse,
    PutLocationRolesRequestBody,
    PutLocationRolesResponse,
    PutLocationRolesResponseData
)
from app.v1.temperature_dashboards.services.temperature_dashboards_service import TemperatureDashboardsService


router = APIRouter()


def _get_location(
    location_id: UUID = Path(alias='id'),
    locations_service: LocationsService = Depends(get_locations_service),
):
    location = locations_service.get_location(location_id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Location not found')
    return location
    

def _authorize_token_for_location_read(
    location: Location = Depends(_get_location),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper),
):
    if not user_access_grants_helper.is_user_authorized_for_location_read(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access location')

def _authorize_token_for_location_update(
    location: Location = Depends(_get_location),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper)
):
    if not user_access_grants_helper.is_user_authorized_for_location_update(access_token_data.user_id, location):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access location')

def _authorize_token_for_organization_read(
    location: Location = Depends(_get_location),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper),
):
    if not user_access_grants_helper.is_user_authorized_for_organization_read(access_token_data.user_id, location.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access location')
    return location

def _authorize_token_for_organization_update(
    location: Location = Depends(_get_location),
    access_token_data: AccessTokenData = Depends(get_access_token_data),
    user_access_grants_helper: UserAccessGrantsHelper = Depends(get_user_access_grants_helper),
):
    if not user_access_grants_helper.is_user_authorized_for_organization_update(access_token_data.user_id, location.organization_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Unauthorized to access location')
    return location
    

def _get_location_dashboard_response_items(
    location: Location,
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
) -> List[LocationDashboardsResponseDataItem]:
    temperature_dashboards = temperature_dashboards_service.get_temperature_dashboards_for_location(location.location_id)
    electricity_dashboards = electricity_dashboards_service.filter_by(location_id=location.location_id)
    hvac_dashboards = hvac_dashboards_service.get_hvac_dashboards_for_location(location.location_id)

    response_items: List[LocationDashboardsResponseDataItem] = list(chain(
        [
            LocationDashboardsResponseDataItem(
                id=dashboard.temperature_dashboard_id,
                name=dashboard.name,
                dashboard_type=LocationDashboardType.TEMPERATURE
            )
            for dashboard in temperature_dashboards
        ],
        [
            LocationDashboardsResponseDataItem(
                id=dashboard.electricity_dashboard_id,
                name=dashboard.name,
                dashboard_type=LocationDashboardType.ELECTRICITY
            )
            for dashboard in electricity_dashboards
        ],
        [
            LocationDashboardsResponseDataItem(
                id=dashboard.hvac_dashboard_id,
                name=dashboard.name,
                dashboard_type=LocationDashboardType.HVAC
            )
            for dashboard in hvac_dashboards
        ],
    ))
    return response_items


@router.get(
    '/locations/{id}',
    dependencies=[Depends(_authorize_token_for_location_read)],
    response_model=GetLocationResponse
)
def get_location(
    location: Location = Depends(_get_location),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
):
    location_dashboard_response_items = _get_location_dashboard_response_items(
        location=location,
        temperature_dashboards_service=temperature_dashboards_service,
        electricity_dashboards_service=electricity_dashboards_service,
        hvac_dashboards_service=hvac_dashboards_service
    )

    return GetLocationResponse(
        code='200',
        message='Success',
        data=GetLocationResponseData(
            id=location.location_id,
            name=location.name,
            city=location.city,
            state=location.state,
            address=location.address,
            country=location.country,
            zip=location.zip_code,
            latitude=location.latitude,
            longitude=location.longitude,
            timezone=location.timezone,
            organization_id=location.organization_id,
            created_at=location.created_at,
            modified_at=location.updated_at,
            dashboards=location_dashboard_response_items
        )
    )


@router.get(
    '/locations/{id}/dashboards',
    dependencies=[Depends(_authorize_token_for_location_read)],
    response_model=GetLocationDashboardsResponse
)
def get_location_dashboards(
    location: Location = Depends(_get_location),
    temperature_dashboards_service: TemperatureDashboardsService = Depends(get_temperature_dashboards_service),
    electricity_dashboards_service: ElectricityDashboardsService = Depends(get_electricity_dashboards_service),
    hvac_dashboards_service: HvacDashboardsService = Depends(get_hvac_dashboards_service),
):
    location_dashboard_response_items = _get_location_dashboard_response_items(
        location=location,
        temperature_dashboards_service=temperature_dashboards_service,
        electricity_dashboards_service=electricity_dashboards_service,
        hvac_dashboards_service=hvac_dashboards_service
    )  

    return GetLocationDashboardsResponse(
        code='200',
        message='Success',
        data=location_dashboard_response_items
    )


@router.put(
    '/locations/{id}/roles',
    dependencies=[Depends(_authorize_token_for_organization_update)],
    response_model=PutLocationRolesResponse
)
def put_location_roles(
    account_id: UUID,
    per_location_roles_request: PutLocationRolesRequestBody,
    location: Location = Depends(_get_location),
    user_location_access_grants_service: UserLocationAccessGrantsService = Depends(get_user_location_access_grants_service),
):
    location_access_grants = list(set([
        location_access_grant
        for per_location_role in per_location_roles_request.roles
        for location_access_grant in per_location_role.get_location_access_grants()
    ]))

    user_location_access_grants_service.set_user_location_access_grants_for_location(
        user_id=account_id,
        location_id=location.location_id,
        access_grants=location_access_grants
    )

    return PutLocationRolesResponse(
        code='200',
        message='Success',
        data=PutLocationRolesResponseData(
            id=uuid4(),  # TODO: Check if this is ok, permission object doesn't exist in this schema
            organization_id=location.organization_id,
            location_id=location.location_id
        )
    )


@router.get(
    '/locations/{id}/roles',
    dependencies=[Depends(_authorize_token_for_organization_read)],
    response_model=GetLocationRolesResponse
)
def get_location_roles(
    account_id: UUID,
    location: Location = Depends(_get_location),
    user_location_access_grants_service: UserLocationAccessGrantsService = Depends(get_user_location_access_grants_service),
    user_organization_access_grants_service: UserOrganizationAccessGrantsService = Depends(get_user_organization_access_grants_service),
):
    user_location_access_grants = set(user_location_access_grants_service.get_user_location_access_grants_for_location(user_id=account_id, location_id=location.location_id))
    per_location_roles: List[PerLocationRole] = []
    for per_location_role in PerLocationRole:
        per_location_role_access_grants = set(per_location_role.get_location_access_grants())
        if user_location_access_grants == per_location_role_access_grants:
            per_location_roles.append(per_location_role)
    
    user_organization_access_grants = set([
        user_organization_access_grant.organization_access_grant
        for user_organization_access_grant in user_organization_access_grants_service.get_user_organization_access_grants(account_id)
        if user_organization_access_grant.organization_id == location.organization_id
    ]).intersection(OrganizationAccessGrant.get_all_location_access_grants())
    all_location_roles: List[AllLocationRole] = []
    for all_location_role in AllLocationRole:
        all_location_role_access_grants = set(all_location_role.get_organization_access_grants())
        if user_organization_access_grants == all_location_role_access_grants:
            all_location_roles.append(all_location_role)
    
    return GetLocationRolesResponse(
        code='200',
        message='Success',
        data=GetLocationRolesResponseData(
            per_location_roles=[role.value for role in per_location_roles],
            all_location_roles=[role.value for role in all_location_roles]
        )
    )


@router.delete(
    '/locations/{id}/roles',
    dependencies=[Depends(_authorize_token_for_organization_update)],
    response_model=DeleteLocationRolesResponse
)
def delete_location_roles(
    account_id: UUID,
    location: Location = Depends(_get_location),
    user_location_access_grants_service: UserLocationAccessGrantsService = Depends(get_user_location_access_grants_service),
):
    user_location_access_grants_service.remove_user_location_access_grants(user_id=account_id, location_id=location.location_id)
    return DeleteLocationRolesResponse(
        code='200',
        message='Success',
        data=None
    )


@router.get(
    '/locations/{id}/operating-hours',
    dependencies=[Depends(_authorize_token_for_location_read)],
    response_model=GetLocationOperatingHoursResponse
)
def get_location_operating_hours(
    location: Location = Depends(_get_location),
    location_operating_hours_service: LocationOperatingHoursService = Depends(get_location_operating_hours_service),
):
    location_operating_hours = location_operating_hours_service.get_location_operating_hours_for_location(location.location_id)
    operating_hours_map = {
        operating_hours.day_of_week: operating_hours
        for operating_hours in location_operating_hours
    }

    return GetLocationOperatingHoursResponse(
        code='200',
        message='Success',
        data=GetLocationOperatingHoursResponseData(
            id=location.location_id,
            monday=ExtendedOperatingHours(
                work_start=monday.work_start_time,
                open=monday.open_time,
                close=monday.close_time,
                work_end=monday.work_end_time
            ) if (monday := operating_hours_map.get(DayOfWeek.MONDAY)) is not None else None,
            tuesday=ExtendedOperatingHours(
                work_start=tuesday.work_start_time,
                open=tuesday.open_time,
                close=tuesday.close_time,
                work_end=tuesday.work_end_time
            ) if (tuesday := operating_hours_map.get(DayOfWeek.TUESDAY)) is not None else None,
            wednesday=ExtendedOperatingHours(
                work_start=wednesday.work_start_time,
                open=wednesday.open_time,
                close=wednesday.close_time,
                work_end=wednesday.work_end_time
            ) if (wednesday := operating_hours_map.get(DayOfWeek.WEDNESDAY)) is not None else None,
            thursday=ExtendedOperatingHours(
                work_start=thursday.work_start_time,
                open=thursday.open_time,
                close=thursday.close_time,
                work_end=thursday.work_end_time
            ) if (thursday := operating_hours_map.get(DayOfWeek.THURSDAY)) is not None else None,
            friday=ExtendedOperatingHours(
                work_start=friday.work_start_time,
                open=friday.open_time,
                close=friday.close_time,
                work_end=friday.work_end_time
            ) if (friday := operating_hours_map.get(DayOfWeek.FRIDAY)) is not None else None,
            saturday=ExtendedOperatingHours(
                work_start=saturday.work_start_time,
                open=saturday.open_time,
                close=saturday.close_time,
                work_end=saturday.work_end_time
            ) if (saturday := operating_hours_map.get(DayOfWeek.SATURDAY)) is not None else None,
            sunday=ExtendedOperatingHours(
                work_start=sunday.work_start_time,
                open=sunday.open_time,
                close=sunday.close_time,
                work_end=sunday.work_end_time
            ) if (sunday := operating_hours_map.get(DayOfWeek.SUNDAY)) is not None else None, 
        )
    )


@router.put(
    '/locations/{id}/operating-hours',
    dependencies=[Depends(_authorize_token_for_location_update)],
    response_model=PutLocationOperatingHoursResponse
)
def put_location_operating_hours(
    operating_hours_update: PutLocationOperatingHoursRequestBody,
    location: Location = Depends(_get_location),
    location_operating_hours_service: LocationOperatingHoursService = Depends(get_location_operating_hours_service),
):
    for day_of_week in DayOfWeek:
        operating_hours_update_for_day: Optional[OperatingHours] = getattr(operating_hours_update, day_of_week.value)
        if operating_hours_update_for_day is None:
            continue

        location_operating_hours_update = LocationOperatingHoursUpdate(
            location_id=location.location_id,
            day_of_week=day_of_week,
            open_time=operating_hours_update_for_day.open,
            close_time=operating_hours_update_for_day.close,
            work_start_time=operating_hours_update_for_day.open,
            work_end_time=operating_hours_update_for_day.close
        )
        location_operating_hours_service.update_location_operating_hours(location_operating_hours_update)
    
    return PutLocationOperatingHoursResponse(
        code='200',
        message='Success',
        data=PulocationOperatingHoursResponseData(
            id=location.location_id
        )
    )


@router.put(
    '/locations/{id}/operating-hours/extended',
    dependencies=[Depends(_authorize_token_for_location_update)],
    response_model=PutLocationOperatingHoursExtendedResponse
)
def put_location_operating_extended_hours(
    operating_hours_update: PutLocationOperatingHoursExtendedRequestBody,
    location: Location = Depends(_get_location),
    location_operating_hours_service: LocationOperatingHoursService = Depends(get_location_operating_hours_service),
):
    for day_of_week in DayOfWeek:
        operating_hours_update_for_day: Optional[ExtendedOperatingHours] = getattr(operating_hours_update, day_of_week.value)
        if operating_hours_update_for_day is None:
            continue

        location_operating_hours_update = LocationOperatingHoursUpdate(
            location_id=location.location_id,
            day_of_week=day_of_week,
            open_time=operating_hours_update_for_day.open,
            close_time=operating_hours_update_for_day.close,
            work_start_time=operating_hours_update_for_day.work_start,
            work_end_time=operating_hours_update_for_day.work_end
        )
        location_operating_hours_service.update_location_operating_hours(location_operating_hours_update)
    
    return PutLocationOperatingHoursExtendedResponse(
        code='200',
        message='Success',
        data=PutLocationOperatingHoursExtendedResponseData(
            id=location.location_id
        )
    )


@router.post(
    '/locations/{id}/electricity-prices',
    dependencies=[Depends(_authorize_token_for_location_update)],
    response_model=PostLocationElectricityPriceResponse
)
def post_electricity_price(
    location_electricity_price_request_body: PostLocationElectricityPriceRequestBody,
    location: Location = Depends(_get_location),
    location_electricity_prices_service: LocationElectricityPricesService = Depends(get_location_electricity_prices_service),
):
    location_electricity_price_create = LocationElectricityPriceCreate(
        location_id=location.location_id,
        comment=location_electricity_price_request_body.comment,
        price_per_kwh=location_electricity_price_request_body.price_per_kwh,
        started_at=location_electricity_price_request_body.effective_from,
        ended_at=None
    )
    location_electricity_price = location_electricity_prices_service.create_location_electricity_price(location_electricity_price_create)

    return PostLocationElectricityPriceResponse(
        code='200',
        message='Success',
        data=PostLocationElectricityPriceResponseData(
            id=location_electricity_price.location_electricity_price_id,
            comment=location_electricity_price.comment,
            effective_from=location_electricity_price.started_at,
            effective_to=location_electricity_price.started_at + timedelta(days=365*100),  # API Schema wants a datetime object instead of None
            price_per_kwh=Decimal(location_electricity_price.price_per_kwh)
        )
    )


@router.get(
    '/locations/{id}/electricity-prices/current',
    dependencies=[Depends(_authorize_token_for_location_read)],
    response_model=PostLocationElectricityPriceResponse
)
def get_current_location_electricity_price(
    location: Location = Depends(_get_location),
    location_electricity_prices_service: LocationElectricityPricesService = Depends(get_location_electricity_prices_service),
):
    location_electricity_price = location_electricity_prices_service.get_current_location_electricity_price(location.location_id)
    if location_electricity_price is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No current electricity price found')

    return PostLocationElectricityPriceResponse(
        code='200',
        message='Success',
        data=PostLocationElectricityPriceResponseData(
            id=location_electricity_price.location_electricity_price_id,
            comment=location_electricity_price.comment,
            effective_from=location_electricity_price.started_at,
            effective_to=location_electricity_price.started_at + timedelta(days=365*100),  # API Schema wants a datetime object instead of None
            price_per_kwh=Decimal(location_electricity_price.price_per_kwh)
        )
    )


@router.post(
    '/locations/{id}/tou-rates',
    dependencies=[Depends(_authorize_token_for_location_update)],
    response_model=PostLocationTimeOfUseRateResponse
)
def post_time_of_use_rate(
    location_time_of_use_rate_request_body: PostLocationTimeOfUseRateRequestBody,
    location: Location = Depends(_get_location),
    location_time_of_use_rates_service: LocationTimeOfUseRatesService = Depends(get_location_time_of_use_rates_service),
    dp_pes_service: DpPesService = Depends(get_dp_pes_service)
):
    location_time_of_use_rate_create = LocationTimeOfUseRateCreate(
        location_id=location.location_id,
        comment=location_time_of_use_rate_request_body.comment,
        price_per_kwh=location_time_of_use_rate_request_body.price_per_kwh,
        start_at=location_time_of_use_rate_request_body.effective_from,
        end_at=location_time_of_use_rate_request_body.effective_to,
        recurs_yearly=location_time_of_use_rate_request_body.recur_yearly,
        day_started_at_seconds=location_time_of_use_rate_request_body.day_seconds_from,
        day_ended_at_seconds=location_time_of_use_rate_request_body.day_seconds_to,
        is_active=not location_time_of_use_rate_request_body.archived,
        days_of_week=[DayOfWeek(day_of_week.lower()) for day_of_week in location_time_of_use_rate_request_body.days_of_week]
    )
    location_time_of_use_rate = location_time_of_use_rates_service.create_location_time_of_use_rate(location_time_of_use_rate_create)

    dp_pes_service.submit_location_metadata(location.location_id)

    return PostLocationTimeOfUseRateResponse(
        code='200',
        message='Success',
        data=PostLocationTimeOfUseRateResponseData(
            id=location_time_of_use_rate.location_time_of_use_rate_id,
            archived=not location_time_of_use_rate.is_active,
            comment=location_time_of_use_rate.comment,
            price_per_kwh=Decimal(location_time_of_use_rate.price_per_kwh),
            effective_from=location_time_of_use_rate.start_at,
            effective_to=location_time_of_use_rate.end_at,
            days_of_week=[day_of_week.value.title() for day_of_week in location_time_of_use_rate.days_of_week],
            day_seconds_from=location_time_of_use_rate.day_started_at_seconds,
            day_seconds_to=location_time_of_use_rate.day_ended_at_seconds,
            recur_yearly=location_time_of_use_rate.recurs_yearly
        )
    )


@router.get(
    '/locations/{id}/tou-rates',
    dependencies=[Depends(_authorize_token_for_location_read)],
    response_model=GetLocationTimeOfUseRatesResponse
)
def get_location_time_of_use_rates(
    location: Location = Depends(_get_location),
    location_time_of_use_rates_service: LocationTimeOfUseRatesService = Depends(get_location_time_of_use_rates_service),
):
    location_time_of_use_rates = location_time_of_use_rates_service.get_location_time_of_use_rates(location.location_id)

    return GetLocationTimeOfUseRatesResponse(
        code='200',
        message='Success',
        data=[
            GetLocationTimeOfUseRateResponseDataItem(
                id=location_time_of_use_rate.location_time_of_use_rate_id,
                archived=not location_time_of_use_rate.is_active,
                comment=location_time_of_use_rate.comment,
                price_per_kwh=Decimal(location_time_of_use_rate.price_per_kwh),
                effective_from=location_time_of_use_rate.start_at,
                effective_to=location_time_of_use_rate.end_at,
                days_of_week=[day_of_week.value.title() for day_of_week in location_time_of_use_rate.days_of_week],
                day_seconds_from=location_time_of_use_rate.day_started_at_seconds,
                day_seconds_to=location_time_of_use_rate.day_ended_at_seconds,
                recur_yearly=location_time_of_use_rate.recurs_yearly
            )
            for location_time_of_use_rate in location_time_of_use_rates
        ]
    )


@router.patch(
    '/locations/{id}/tou-rates/{tou_rate_id}',
    dependencies=[Depends(_authorize_token_for_location_update), Depends(_get_location)],
    response_model=PatchLocationTimeOfUseRateResponse
)
def patch_location_time_of_use_rate(
    tou_rate_id: UUID,
    location_time_of_use_rate_request_body: PatchLocationTimeOfUseRateRequestBody,
    location: Location = Depends(_get_location),
    location_time_of_use_rates_service: LocationTimeOfUseRatesService = Depends(get_location_time_of_use_rates_service),
    dp_pes_service: DpPesService = Depends(get_dp_pes_service)
):
    location_time_of_use_rate_update = LocationTimeOfUseRateUpdate(
        location_time_of_use_rate_id=tou_rate_id,
        is_active=not location_time_of_use_rate_request_body.archived
    )

    location_time_of_use_rate = location_time_of_use_rates_service.update_location_time_of_use_rate(
        location_time_of_use_rate_update
    )

    dp_pes_service.submit_location_metadata(location.location_id)
    
    return PatchLocationTimeOfUseRateResponse(
        code='200',
        message='Success',
        data=PatchLocationTimeOfUseRateResponseData(
            id=location_time_of_use_rate.location_time_of_use_rate_id,
            archived=not location_time_of_use_rate.is_active,
            comment=location_time_of_use_rate.comment,
            price_per_kwh=Decimal(location_time_of_use_rate.price_per_kwh),
            effective_from=location_time_of_use_rate.start_at,
            effective_to=location_time_of_use_rate.end_at,
            days_of_week=[day_of_week.value.title() for day_of_week in location_time_of_use_rate.days_of_week],
            day_seconds_from=location_time_of_use_rate.day_started_at_seconds,
            day_seconds_to=location_time_of_use_rate.day_ended_at_seconds,
            recur_yearly=location_time_of_use_rate.recurs_yearly
        )
    )


@router.get(
    '/locations/{id}/electricity-usage-mtd',
    dependencies=[Depends(_authorize_token_for_location_read)],
    response_model=GetLocationElectricityUsageMtdResponse
)
def get_location_electricity_usage_mtd(
    location: Location = Depends(_get_location),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    timestream_electricity_circuit_measurements_service: TimestreamElectricityCircuitMeasurementsService = Depends(get_timestream_electricity_circuit_measurements_service),
    location_aggregated_data_cache: Cache = Depends(get_location_aggregated_data_cache),
):
    local_now: datetime = datetime.now(tz=ZoneInfo(location.timezone))
    current_hour: datetime = local_now.replace(minute=0, second=0, microsecond=0).astimezone(timezone.utc)
    current_month_start: datetime = local_now.replace(day=1, hour=0, minute=0, second=0, microsecond=0).astimezone(timezone.utc)

    cache_key = f"locations::{location.location_id!s}::electricity-usage-mtd::{current_month_start.isoformat()}"
    cached_total_usage = location_aggregated_data_cache.get(key=cache_key)
    
    if cached_total_usage is not None:
        return GetLocationElectricityUsageMtdResponse(
            data=GetLocationElectricityUsageMtdResponseData(
                kwh=cached_total_usage
            ),
            code='200',
            message='success'
        )

    location_mains = circuits_service.get_circuits_of_type_for_location(location.location_id, CircuitTypeEnum.main)
    if len(location_mains) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no_mains_available')
    
    usage_records = timestream_electricity_circuit_measurements_service.get_energy_table_circuits_energy(
        circuit_ids=[circuit.circuit_id for circuit in location_mains],
        start_datetime=current_month_start,
        end_datetime=current_hour
    )
    total_usage = sum([usage_record.usage.kwh for usage_record in usage_records])
    
    location_aggregated_data_cache.set(
        key=cache_key,
        value=total_usage,
        expire_in_seconds=int(timedelta(hours=1).total_seconds())
    )
    
    return GetLocationElectricityUsageMtdResponse(
        data=GetLocationElectricityUsageMtdResponseData(
            kwh=total_usage
        ),
        code='200',
        message='success'
    )


@router.get(
    '/locations/{id}/alerts',
    dependencies=[Depends(_authorize_token_for_location_read)],
    response_model=GetLocationAlertsResponse
)
def get_location_alerts(
    location: Location = Depends(_get_location),
    temperature_sensor_place_alerts_service: TemperatureSensorPlaceAlertsService = Depends(get_temperature_sensor_place_alerts_service),
):
    active_alerts = temperature_sensor_place_alerts_service.get_active_temperature_sensor_place_alerts_for_location(location.location_id)
    return GetLocationAlertsResponse(
        data=GetLocationAlertsResponseData(
            ongoing_alerts=len(active_alerts)
        ),
        code='200',
        message='success'
    )
    
@router.get(
    '/locations/{id}/usage-change',
    dependencies=[Depends(_authorize_token_for_location_read)],
    response_model=GetLocationUsageChangeResponse
)
def get_location_usage_change(
    location: Location = Depends(_get_location),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    location_aggregated_data_cache: Cache = Depends(get_location_aggregated_data_cache),
    timestream_electricity_circuit_measurements_service: TimestreamElectricityCircuitMeasurementsService = Depends(get_timestream_electricity_circuit_measurements_service),
):
    location_mains = circuits_service.get_circuits_of_type_for_location(location.location_id, CircuitTypeEnum.main)
    if len(location_mains) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no_mains_available')

    def _get_electricity_usage_for_period(
        start_datetime: datetime,
        end_datetime: datetime
    ) -> float:
        cache_key = f"locations::{location.location_id!s}::usage-change::{start_datetime.isoformat()}"
        cached_usage = location_aggregated_data_cache.get(key=cache_key)
        if cached_usage is None:
            usage_records = timestream_electricity_circuit_measurements_service.get_energy_table_circuits_energy(
                circuit_ids=[circuit.circuit_id for circuit in location_mains],
                start_datetime=start_datetime,
                end_datetime=end_datetime
            )
            usage = sum([usage_record.usage.kwh for usage_record in usage_records])
            location_aggregated_data_cache.set(
                key=cache_key,
                value=usage,
                expire_in_seconds=int(timedelta(days=8).total_seconds())
            )
        else:
            usage = float(cached_usage)
        return usage

    local_now: datetime = datetime.now(tz=ZoneInfo(location.timezone))
    yesterday_end: datetime = local_now - timedelta(days=1)

    current_week_period = (
        (yesterday_end - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0),
         yesterday_end.replace(hour=23, minute=59, second=59, microsecond=999999)
    )
    current_week_usage = _get_electricity_usage_for_period(current_week_period[0].astimezone(tz=timezone.utc), current_week_period[1].astimezone(tz=timezone.utc))

    previous_week_period = (
        current_week_period[0] - timedelta(days=7),
        current_week_period[1] - timedelta(days=7)
    )
    previous_week_usage = _get_electricity_usage_for_period(previous_week_period[0].astimezone(tz=timezone.utc), previous_week_period[1].astimezone(tz=timezone.utc))

    return GetLocationUsageChangeResponse(
        data=GetLocationUsageChangeResponseData(
            current_week_kwh=current_week_usage,
            previous_week_kwh=previous_week_usage,
        ),
        code='200',
        message='success'
    )


@router.get(
    '/locations/{id}/energy-usage-trend',
    dependencies=[Depends(_authorize_token_for_location_read)],
    response_model=GetLocationEnergyUsageTrendResponse
)
def get_location_energy_usage_trend(
    location: Location = Depends(_get_location),
    circuits_service: CircuitsService = Depends(get_circuits_service),
    location_aggregated_data_cache: Cache = Depends(get_location_aggregated_data_cache),
    timestream_electricity_circuit_measurements_service: TimestreamElectricityCircuitMeasurementsService = Depends(get_timestream_electricity_circuit_measurements_service),
):
    location_mains = circuits_service.get_circuits_of_type_for_location(location.location_id, CircuitTypeEnum.main)
    if len(location_mains) == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no_mains_available')
    
    def _get_electricity_usage_for_period(
        start_datetime: datetime,
        end_datetime: datetime
    ) -> float:
        cache_key = f"locations::{location.location_id!s}::energy-usage-trend::{start_datetime}"
        cached_usage = location_aggregated_data_cache.get(key=cache_key)
        if cached_usage is None:
            usage_records = timestream_electricity_circuit_measurements_service.get_energy_table_circuits_energy(
                circuit_ids=[circuit.circuit_id for circuit in location_mains],
                start_datetime=start_datetime,
                end_datetime=end_datetime
            )
            usage = sum([usage_record.usage.kwh for usage_record in usage_records])
            location_aggregated_data_cache.set(
                key=cache_key,
                value=usage,
                expire_in_seconds=int(timedelta(days=4).total_seconds())
            )
        else:
            usage = float(cached_usage)
        return usage

    yesterday_local: datetime = datetime.now(tz=ZoneInfo(location.timezone)).replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    yesterday_start_local = yesterday_local.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end_local = yesterday_local.replace(hour=23, minute=59, second=59, microsecond=999999)
    yesterday_start = yesterday_start_local.astimezone(timezone.utc)
    yesterday_end = yesterday_end_local.astimezone(timezone.utc)

    datapoints: List[Tuple[datetime, float]] = [
        (yesterday_start - timedelta(days=2), _get_electricity_usage_for_period(yesterday_start - timedelta(days=2), yesterday_end - timedelta(days=2))),
        (yesterday_start - timedelta(days=1), _get_electricity_usage_for_period(yesterday_start - timedelta(days=1), yesterday_end - timedelta(days=1))),
        (yesterday_start, _get_electricity_usage_for_period(yesterday_start, yesterday_end))
    ]

    return GetLocationEnergyUsageTrendResponse(
        data=GetLocationEnergyUsageTrendResponseData(
            datapoints=datapoints
        ),
        code='200',
        message='success'
    )
