from fastapi import APIRouter

from app.v3_adapter.accounts.router import router as accounts_router
from app.v3_adapter.auth.router import router as auth_router
from app.v3_adapter.circuits.router import router as circuits_router
from app.v3_adapter.electric_dashboards.router import router as electric_dashboards_router
from app.v3_adapter.electric_widgets.router import router as electric_widgets_router
from app.v3_adapter.hvac_dashboards.router import router as hvac_dashboards_router
from app.v3_adapter.hvac_schedules.router import router as hvac_schedules
from app.v3_adapter.hvac_widgets.router import router as hvac_widgets_router
from app.v3_adapter.locations.router import router as locations_router
from app.v3_adapter.operating_range_notification_settings.router import router as operating_range_notification_settings_router
from app.v3_adapter.organizations.router import router as organizations_router
from app.v3_adapter.temperature_dashboards.router import router as temperature_dashboards_router
from app.v3_adapter.temperature_widgets.router import router as temperature_widgets_router
from app.v3_adapter.thermostats.router import router as thermostats_router

router = APIRouter(tags=['v3'])

router.include_router(accounts_router)
router.include_router(auth_router)
router.include_router(circuits_router)
router.include_router(electric_dashboards_router)
router.include_router(electric_widgets_router)
router.include_router(hvac_dashboards_router)
router.include_router(hvac_schedules)
router.include_router(hvac_widgets_router)
router.include_router(locations_router)
router.include_router(operating_range_notification_settings_router)
router.include_router(organizations_router)
router.include_router(temperature_dashboards_router)
router.include_router(temperature_widgets_router)
router.include_router(thermostats_router)
