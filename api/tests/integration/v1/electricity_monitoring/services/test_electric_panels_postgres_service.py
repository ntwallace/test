from uuid import uuid4
import pytest
from sqlalchemy.orm import Session

from app.v1.electricity_monitoring.models.electric_panel import ElectricPanel
from app.v1.electricity_monitoring.repositories.electric_panels_repository import PostgresElectricPanelsRepository
from app.v1.electricity_monitoring.schemas.electric_panel import ElectricPanelCreate
from app.v1.electricity_monitoring.services.electric_panels import ElectricPanelsService


def test_create_electric_sensor_inserts_new_model(db_session_for_tests: Session):
    service = ElectricPanelsService(
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    electric_panel_create = ElectricPanelCreate(
        name="Test Electric Panel",
        panel_type="mdp",
        location_id=uuid4(),
        breaker_count=1,
        electric_panel_id=uuid4()
    )
    electric_panel = service.create_electric_panel(electric_panel_create)
    electric_panels_model = db_session_for_tests.query(ElectricPanel).all()
    assert len(electric_panels_model) == 1
    electric_panel_model = electric_panels_model[0]
    assert electric_panel_model.electric_panel_id == electric_panel.electric_panel_id
    assert electric_panel_model.name == electric_panel.name
    assert electric_panel_model.panel_type == electric_panel.panel_type
    assert electric_panel_model.location_id == electric_panel.location_id
    assert electric_panel_model.breaker_count == electric_panel.breaker_count
    assert electric_panel_model.created_at == electric_panel.created_at
    assert electric_panel_model.updated_at == electric_panel.updated_at


def test_create_electric_panel_raises_error_if_electric_panel_exists(db_session_for_tests: Session):
    service = ElectricPanelsService(
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    electric_panel_create = ElectricPanelCreate(
        name="Test Electric Panel",
        panel_type="mdp",
        location_id=uuid4(),
        breaker_count=1,
        electric_panel_id=uuid4()
    )
    service.create_electric_panel(electric_panel_create)
    with pytest.raises(ValueError):
        service.create_electric_panel(electric_panel_create)


def test_get_electric_sensor_by_id_returns_correct_sensor(db_session_for_tests: Session):
    service = ElectricPanelsService(
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    electric_panel_create = ElectricPanelCreate(
        name="Test Electric Panel",
        panel_type="mdp",
        location_id=uuid4(),
        breaker_count=1,
        electric_panel_id=uuid4()
    )
    electric_panel = service.create_electric_panel(electric_panel_create)
    electric_panel_model = service.get_electric_panel_by_id(electric_panel.electric_panel_id)
    assert electric_panel_model.electric_panel_id == electric_panel.electric_panel_id
    assert electric_panel_model.name == electric_panel.name
    assert electric_panel_model.panel_type == electric_panel.panel_type
    assert electric_panel_model.location_id == electric_panel.location_id
    assert electric_panel_model.breaker_count == electric_panel.breaker_count
    assert electric_panel_model.created_at == electric_panel.created_at
    assert electric_panel_model.updated_at == electric_panel.updated_at


def test_get_electric_panel_by_id_returns_none_if_electric_panel_does_not_exist(db_session_for_tests: Session):
    service = ElectricPanelsService(
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    electric_panel_model = service.get_electric_panel_by_id(uuid4())
    assert electric_panel_model is None


def test_get_electric_sensor_by_attributes_returns_correct_sensor(db_session_for_tests: Session):
    service = ElectricPanelsService(
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    location_id = uuid4()
    electric_panel_create = ElectricPanelCreate(
        name="Test Electric Panel",
        panel_type="mdp",
        location_id=location_id,
        breaker_count=1,
        electric_panel_id=uuid4()
    )
    electric_panel = service.create_electric_panel(electric_panel_create)
    electric_panel_model = service.get_electric_panel_by_attributes(
        name=electric_panel.name,
        location_id=location_id
    )
    assert electric_panel_model.electric_panel_id == electric_panel.electric_panel_id
    assert electric_panel_model.name == electric_panel.name
    assert electric_panel_model.panel_type == electric_panel.panel_type
    assert electric_panel_model.location_id == electric_panel.location_id
    assert electric_panel_model.breaker_count == electric_panel.breaker_count
    assert electric_panel_model.created_at == electric_panel.created_at
    assert electric_panel_model.updated_at == electric_panel.updated_at


def test_get_electric_panel_by_attributes_returns_none_if_panel_does_not_exist(db_session_for_tests: Session):
    service = ElectricPanelsService(
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    electric_panel_model = service.get_electric_panel_by_attributes(
        name="Test Electric Panel",
        location_id=uuid4()
    )
    assert electric_panel_model is None


def test_get_electric_panels_by_location_returns_correct_sensors(db_session_for_tests: Session):
    service = ElectricPanelsService(
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    location_id = uuid4()
    electric_panel_create = ElectricPanelCreate(
        name="Test Electric Panel",
        panel_type="mdp",
        location_id=location_id,
        breaker_count=1,
        electric_panel_id=uuid4()
    )
    electric_panel = service.create_electric_panel(electric_panel_create)
    electric_panels = service.get_electric_panels_by_location(location_id)
    assert len(electric_panels) == 1
    electric_panel_model = electric_panels[0]
    assert electric_panel_model.electric_panel_id == electric_panel.electric_panel_id
    assert electric_panel_model.name == electric_panel.name
    assert electric_panel_model.panel_type == electric_panel.panel_type
    assert electric_panel_model.location_id == electric_panel.location_id
    assert electric_panel_model.breaker_count == electric_panel.breaker_count
    assert electric_panel_model.created_at == electric_panel.created_at
    assert electric_panel_model.updated_at == electric_panel.updated_at


def test_delete_electric_panel_deletes_correct_panel(db_session_for_tests: Session):
    service = ElectricPanelsService(
        electric_panels_repository=PostgresElectricPanelsRepository(db_session_for_tests)
    )
    electric_panel_create = ElectricPanelCreate(
        name="Test Electric Panel",
        panel_type="mdp",
        location_id=uuid4(),
        breaker_count=1,
        electric_panel_id=uuid4()
    )
    electric_panel = service.create_electric_panel(electric_panel_create)
    service.delete_electric_panel(electric_panel.electric_panel_id)
    electric_panel_model = service.get_electric_panel_by_id(electric_panel.electric_panel_id)
    assert electric_panel_model is None
