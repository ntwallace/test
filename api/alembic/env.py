import os

from logging.config import fileConfig

import alembic_postgresql_enum

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool


load_dotenv()

POWERX_DATABASE_HOST = os.environ['POWERX_DATABASE_HOST']
POWERX_DATABASE_PORT = os.environ['POWERX_DATABASE_PORT']
POWERX_DATABASE_USER = os.environ['POWERX_DATABASE_USER']
POWERX_DATABASE_PASSWORD = os.environ['POWERX_DATABASE_PASSWORD']
POWERX_DATABASE_NAME = os.environ['POWERX_DATABASE_NAME']
POWERX_DATABASE_URL = f"postgresql+psycopg://{POWERX_DATABASE_USER}:{POWERX_DATABASE_PASSWORD}@{POWERX_DATABASE_HOST}:{POWERX_DATABASE_PORT}/{POWERX_DATABASE_NAME}"


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
from app.v1.locations.models.location import Location
from app.v1.locations.models.location_operating_hours import LocationOperatingHours
from app.v1.locations.models.location_electricity_price import LocationElectricityPrice
from app.v1.locations.models.location_time_of_use_rate import LocationTimeOfUseRate
from app.v1.organizations.models.organization import Organization
from app.v1.organizations.models.organization_user import OrganizationUser
from app.v1.users.models.user import User

from app.v1.auth.models.access_role_access_scope import AccessRoleAccessScope
from app.v1.auth.models.access_role import AccessRole
from app.v1.auth.models.api_key import APIKey
from app.v1.auth.models.api_key_access_scope import APIKeyAccessScope
from app.v1.auth.models.api_key_access_role import APIKeyAccessRole
from app.v1.auth.models.user_access_scope import UserAccessScope
from app.v1.auth.models.user_access_role import UserAccessRole
from app.v1.auth.models.user_organization_access_grant import UserOrganizationAccessGrant
from app.v1.auth.models.user_location_access_grant import UserLocationAccessGrant

from app.v1.electricity_monitoring.models.circuit import Circuit
from app.v1.electricity_monitoring.models.clamp import Clamp
from app.v1.electricity_monitoring.models.electric_panel import ElectricPanel
from app.v1.electricity_monitoring.models.electric_sensor import ElectricSensor

from app.v1.appliances.models.appliance_type import ApplianceType
from app.v1.appliances.models.appliance import Appliance

from app.v1.hvac.models.hvac_zone import HvacZone
from app.v1.hvac.models.hvac_zone_equipment import HvacZoneEquipment
from app.v1.hvac.models.hvac_equipment_type import HvacEquipmentTypes
from app.v1.hvac.models.hvac_zone_temperature_sensor import HvacZoneTemperatureSensors
from app.v1.hvac.models.thermostat import Thermostat

from app.v1.mesh_network.models.gateway import Gateway
from app.v1.mesh_network.models.node import Node

from app.v1.temperature_monitoring.models.temperature_sensor import TemperatureSensor
from app.v1.temperature_monitoring.models.temperature_sensor_place import TemperatureSensorPlace
from app.v1.temperature_monitoring.models.temperature_range import TemperatureRange
from app.v1.temperature_monitoring.models.temperature_sensor_place_alert import TemperatureSensorPlaceAlert

from app.v3_adapter.auth.models import UserAuthResetCode

from app.v1.electricity_dashboards.models.electricity_dashboard import ElectricityDashboard
from app.v1.electricity_dashboards.models.energy_consumption_breakdown_electric_widget import EnergyConsumptionBreakdownElectricWidget
from app.v1.electricity_dashboards.models.energy_load_curve_electric_widget import EnergyLoadCurveElectricWidget
from app.v1.electricity_dashboards.models.panel_system_health_electric_widget import PanelSystemHealthElectricWidget

from app.v1.temperature_dashboards.models.temperature_dashboard import TemperatureDashboard
from app.v1.temperature_dashboards.models.temeprature_unit_widget import TemperatureUnitWidget

from app.v1.hvac_dashboards.models.hvac_dashboard import HvacDashboard
from app.v1.hvac.models.hvac_schedule import HvacSchedule, HvacScheduleEvent
from app.v1.hvac_dashboards.models.control_zone_hvac_widget import ControlZoneHvacWidget, ControlZoneTemperaturePlaceLink
from app.v1.hvac.models.hvac_hold import HvacHold

from app.v3_adapter.operating_range_notification_settings.models import OperatingRangeNotificationSettings

from app.database import Base
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
config.set_main_option("sqlalchemy.url", POWERX_DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
