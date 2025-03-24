from fastapi import APIRouter

from app.v1.auth.router import router as auth_router
from app.v1.locations.locations_router import router as locations_router
from app.v1.locations.location_circuits_router import router as location_circuits_router
from app.v1.locations.location_hvac_zones_router import router as location_hvac_zones_router
from app.v1.locations.location_temperature_sensor_places_router import router as location_temperature_sensor_places_router
from app.v1.organizations.router import router as organizations_router
from app.v1.users.router import router as users_router
from app.v1.appliances.appliance_type_router import router as appliance_type_router
from app.v1.appliances.appliances_router import router as appliances_router
from app.v1.electricity_dashboards.electricity_dashboards_router import router as electricity_dashboards_router
from app.v1.electricity_monitoring.electric_panels_router import router as electric_panels_router
from app.v1.electricity_monitoring.electric_sensors_router import router as electric_sensors_router
from app.v1.electricity_monitoring.circuits_router import router as circuits_router
from app.v1.electricity_monitoring.clamps_router import router as clamps_router
from app.v1.hvac_dashboards.control_zone_hvac_widgets_router import router as control_zone_hvac_widgets_router
from app.v1.hvac_dashboards.hvac_dashboards_router import router as hvac_dashboards_router
from app.v1.mesh_network.gateways_router import router as gateways_router
from app.v1.mesh_network.nodes_router import router as nodes_router
from app.v1.temperature_dashboards.temperature_dashboards_router import router as temperature_dashboards_router
from app.v1.temperature_dashboards.temperature_unit_widgets_router import router as temperature_unit_widgets_router
from app.v1.temperature_monitoring.temperature_sensors_router import router as temperature_sensors_router
from app.v1.temperature_monitoring.temperature_sensor_places_router import router as temperature_sensor_places_router
from app.v1.hvac.hvac_zones_router import router as hvac_zones_router
from app.v1.hvac.hvac_zone_equipment_router import router as hvac_zone_equipment_router
from app.v1.hvac.hvac_equipment_types_router import router as hvac_equipment_types_router
from app.v1.hvac.hvac_zone_temperature_sensors_router import router as hvac_zone_temperature_sensors_router
from app.v1.hvac.thermostats_router import router as thermostats_router
from app.v1.devices.router import router as devices_router


router = APIRouter()

# Auth
router.include_router(auth_router, prefix='/auth')

# Locations
router.include_router(locations_router, prefix='/locations')
router.include_router(location_circuits_router, prefix='/locations')
router.include_router(location_hvac_zones_router, prefix='/locations')
router.include_router(location_temperature_sensor_places_router, prefix='/locations')

# Organizations
router.include_router(organizations_router, prefix='/organizations')

# Users
router.include_router(users_router, prefix='/users')

# Appliances
router.include_router(appliance_type_router, prefix='/appliance-types')
router.include_router(appliances_router, prefix='/appliances')

# Electricity Dashboards
router.include_router(electricity_dashboards_router, prefix='/electricity-dashboards')

# Electricity Monitoring
router.include_router(electric_panels_router, prefix='/electric-panels')
router.include_router(electric_sensors_router, prefix='/electric-sensors')
router.include_router(circuits_router, prefix='/circuits')
router.include_router(clamps_router, prefix='/clamps')

# Hvac Dashboards
router.include_router(hvac_dashboards_router, prefix='/hvac-dashboards')
router.include_router(control_zone_hvac_widgets_router, prefix='/control-zone-hvac-widgets')

# Mesh Networks
router.include_router(gateways_router, prefix='/gateways')
router.include_router(nodes_router, prefix='/nodes')

# Temperature Dashboards
router.include_router(temperature_dashboards_router, prefix='/temperature-dashboards')
router.include_router(temperature_unit_widgets_router, prefix='/temperature-unit-widgets')

# Temperature Monitoring
router.include_router(temperature_sensors_router, prefix='/temperature-sensors')
router.include_router(temperature_sensor_places_router, prefix='/temperature-sensor-places')

# HVAC
router.include_router(hvac_zones_router, prefix='/hvac-zones')
router.include_router(hvac_zone_equipment_router, prefix='/hvac-zone-equipment')
router.include_router(hvac_equipment_types_router, prefix='/hvac-equipment-types')
router.include_router(hvac_zone_temperature_sensors_router, prefix='/hvac-zone-temperature-sensors')
router.include_router(thermostats_router, prefix='/thermostats')

# STATUS
router.include_router(devices_router, prefix='/devices')
