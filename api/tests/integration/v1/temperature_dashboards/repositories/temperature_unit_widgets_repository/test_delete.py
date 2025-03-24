from uuid import uuid4

from sqlalchemy.orm import Session

from app.v1.temperature_dashboards.models.temeprature_unit_widget import TemperatureUnitWidget as TemperatureUnitWidgetModel
from app.v1.temperature_dashboards.repositories.temperature_unit_widgets_repository import PostgresTemperatureUnitWidgetsRepository
from app.v1.temperature_dashboards.schemas.temperature_unit_widget import TemperatureUnitWidgetCreate, ApplianceType


def test_deletes_existing_temperature_unit_widget(db_session_for_tests: Session):
    
    temperature_unit_widgets_repository = PostgresTemperatureUnitWidgetsRepository(db_session_for_tests)

    temperature_unit_widget = temperature_unit_widgets_repository.create(TemperatureUnitWidgetCreate(
        name='Test temperature unit widget',
        low_c=0.0,
        high_c=100.0,
        alert_threshold_s=60,
        appliance_type=ApplianceType.FREEZER,
        temperature_sensor_place_id=uuid4(),
        temperature_dashboard_id=uuid4()
    ))
    temperature_unit_widgets_repository.create(TemperatureUnitWidgetCreate(
        name='Test temperature unit widget 2',
        low_c=0.0,
        high_c=100.0,
        alert_threshold_s=60,
        appliance_type=ApplianceType.FREEZER,
        temperature_sensor_place_id=uuid4(),
        temperature_dashboard_id=uuid4()
    ))

    temperature_unit_widgets_repository.delete(temperature_unit_widget.temperature_unit_widget_id)

    temperature_unit_widgets_db = db_session_for_tests.query(TemperatureUnitWidgetModel).all()

    assert len(temperature_unit_widgets_db) == 1
    temperature_unit_widget_db = temperature_unit_widgets_db[0]

    assert temperature_unit_widget_db.name == 'Test temperature unit widget 2'
