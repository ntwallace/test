import argparse
from datetime import datetime, time
import json
import logging
import os
from typing import List
from uuid import UUID

from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import sessionmaker

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
from app.v1.temperature_dashboards.models.temperature_dashboard import TemperatureDashboard
from app.v1.temperature_monitoring.models.temperature_range import TemperatureRange
from app.v1.temperature_monitoring.models.temperature_sensor import TemperatureSensor
from app.v1.temperature_monitoring.models.temperature_sensor_place import TemperatureSensorPlace
from app.v1.temperature_monitoring.models.temperature_sensor_place_alert import TemperatureSensorPlaceAlert
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


def main(location_id: UUID):
    base_dir = f'.tmp/{location_id}'
    filename_to_model_classes = {
        'organizations': Organization,
        'locations': Location,
        'electric_panels': ElectricPanel,
        'circuits': Circuit,
        'clamps': Clamp,
        'electric_sensors': ElectricSensor,
        'gateways': Gateway,
        'hvac_zones': HvacZone,
        'location_electricity_prices': LocationElectricityPrice,
        'location_operating_hours': LocationOperatingHours,
        'location_time_of_use_rates': LocationTimeOfUseRate,
        'nodes': Node,
        'temperature_ranges': TemperatureRange,
        'temperature_sensor_place_alerts': TemperatureSensorPlaceAlert,
        'temperature_sensor_places': TemperatureSensorPlace,
        'temperature_sensors': TemperatureSensor,
        'thermostats': Thermostat,
        'electric_dashboards': ElectricityDashboard,
        'energy_consumption_breakdown_widgets': EnergyConsumptionBreakdownElectricWidget,
        'energy_load_curve_widgets': EnergyLoadCurveElectricWidget,
        'panel_system_health_widgets': PanelSystemHealthElectricWidget,
        'hvac_dashboards': HvacDashboard,
        'control_zone_widgets': ControlZoneHvacWidget,
        'hvac_holds': HvacHold,
        'hvac_schedule_events': HvacScheduleEvent,
        'hvac_schedules': HvacSchedule,
        'temperature_dashboards': TemperatureDashboard,
        'temperature_unit_widgets': TemperatureUnitWidget,
    }

    try:
        for filename, model_class in filename_to_model_classes.items():
            models = deserialize_models_from_file(os.path.join(base_dir, f'{filename}.json'), model_class)
            logger.info(f'Deserialized {len(models)} instances of {model_class.__name__}')
            if not DRY_RUN:
                logger.info(f'Loading {len(models)} instances of {model_class.__name__} to the database')
                loaded_model_count = load_models_to_db(models)
                logger.info(f'Loaded {loaded_model_count} instances of {model_class.__name__} to the database')
        logger.info('Committing changes to the database')
        postgres_session.commit()
        logger.info('Changes committed to the database')
        
    except Exception as e:
        logger.error("An error occurred while loading data.")
        logger.error(e)
        postgres_session.rollback()

def load_models_to_db(models: List):
    """
    Load a list of SQLAlchemy model instances into the database, ignores duplicates.

    :param models: List of SQLAlchemy model instances to be added to the database.
    """
    if len(models) == 0:
        return
    count = 0
    for model in models:
        try:
            model_class = model.__class__

            # Build a filter dynamically from the instance's column values
            filters = []
            for column in inspect(model_class).columns:
                column_value = getattr(model, column.name)
                filters.append(column == column_value)

            # Query the target database
            query = postgres_session.query(model_class).filter(*filters)
            scalar = postgres_session.query(query.exists()).scalar()
            if not scalar:
                postgres_session.add(model)
                count += 1
        except Exception as e:
            logger.error(f"Error adding {model} to the session: {e}")
            continue
    return count

def deserialize_models_from_file(file_path: str, model_class):
    """
    Read serialized data from a JSON file and convert it into SQLAlchemy model instances.

    :param file_path: Path to the JSON file containing serialized data.
    :param model_class: SQLAlchemy model class to deserialize into.
    :return: List of SQLAlchemy model instances.
    """
    logger.debug(f'Deserializing data from {file_path} into {model_class.__name__}')
    with open(file_path, "r") as json_file:
        serialized_data = json.load(json_file)
    
    deserialized_models = []
    for data in serialized_data:
        transformed_data = {
            key: deserialize_value(value, model_class.__table__.columns[key].type.python_type)
            for key, value in data.items()
        }
        model_instance = model_class(**transformed_data)
        logger.debug(f'Deserialized {model_instance.__dict__}')
        deserialized_models.append(model_instance)

    return deserialized_models

def deserialize_value(value, expected_type):
    if value is None:
        return None

    if expected_type == datetime:
        # Convert ISO 8601 string to datetime object
        return datetime.fromisoformat(value)
    elif expected_type == time:
        # Convert ISO 8601 string to time object
        return time.fromisoformat(value)
    elif expected_type == UUID:
        # Convert string to UUID
        return UUID(value)
    else:
        # Return the value as is for other types
        return value

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Load location data from files to a postgres database."
    )
    parser.add_argument(
        'location_id',
        type=str,
        help='Location ID'
    )
    args = parser.parse_args()
    arg_location_id = UUID(args.location_id)
    main(location_id=arg_location_id)
