from uuid import uuid4

import pytest

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.mesh_network.models.gateway import Gateway
from app.v1.mesh_network.repositories.gateways_repository import PostgresGatewaysRepository
from app.v1.mesh_network.schemas.gateway import GatewayCreate
from app.v1.mesh_network.services.gateways import GatewaysService


@pytest.fixture
def gateways_service(db_session_for_tests: Session):
    return GatewaysService(
        gateways_repository=PostgresGatewaysRepository(db_session_for_tests)
    )


def test_create_gateway_inserts_new_model(gateways_service: GatewaysService, db_session_for_tests: Session):
    gateway_create = GatewayCreate(
        name="Test Gateway",
        duid="test_duid",
        organization_id=uuid4(),
        location_id=uuid4(),
        gateway_id=uuid4()
    )
    gateway = gateways_service.create_gateway(gateway_create)
    gateway_models = db_session_for_tests.query(Gateway).all()
    assert len(gateway_models) == 1
    gateway_model = gateway_models[0]
    assert gateway_model.gateway_id == gateway.gateway_id
    assert gateway_model.name == gateway.name
    assert gateway_model.location_id == gateway.location_id
    assert gateway_model.created_at == gateway.created_at
    assert gateway_model.updated_at == gateway.updated_at


def test_create_gateway_raises_error_if_gateway_exists(gateways_service: GatewaysService):
    gateway_create = GatewayCreate(
        name="Test Gateway",
        duid="test_duid",
        organization_id=uuid4(),
        location_id=uuid4(),
        gateway_id=uuid4()
    )
    gateways_service.create_gateway(gateway_create)
    with pytest.raises(IntegrityError):
        gateways_service.create_gateway(gateway_create)


def test_get_gateway_by_id_returns_correct_gateway(gateways_service: GatewaysService):
    gateway_create = GatewayCreate(
        name="Test Gateway",
        duid="test_duid",
        organization_id=uuid4(),
        location_id=uuid4(),
        gateway_id=uuid4()
    )
    gateway = gateways_service.create_gateway(gateway_create)
    gateway_model = gateways_service.get_gateway_by_gateway_id(gateway.gateway_id)
    assert gateway_model == gateway


def test_get_gateway_by_id_returns_none_if_gateway_not_found(gateways_service: GatewaysService):
    gateway_create = GatewayCreate(
        name="Test Gateway",
        duid="test_duid",
        organization_id=uuid4(),
        location_id=uuid4(),
        gateway_id=uuid4()
    )
    gateways_service.create_gateway(gateway_create)
    gateway_model = gateways_service.get_gateway_by_gateway_id(uuid4())
    assert gateway_model is None


def test_get_gateways_by_location_id_returns_correct_gateways(gateways_service: GatewaysService):
    location_id = uuid4()
    gateways_service.create_gateway(GatewayCreate(
        name="Test Gateway 1",
        duid="test_duid1",
        organization_id=uuid4(),
        location_id=uuid4(),
        gateway_id=uuid4()
    ))
    gateway_create = GatewayCreate(
        name="Test Gateway 2",
        duid="test_duid2",
        organization_id=uuid4(),
        location_id=location_id,
        gateway_id=uuid4()
    )
    gateway = gateways_service.create_gateway(gateway_create)
    gateways = gateways_service.get_gateways_by_location_id(location_id)
    assert gateways == [gateway]


def test_get_gateways_by_location_id_returns_empty_list_if_no_gateways(gateways_service: GatewaysService):
    gateways_service.create_gateway(
        GatewayCreate(
            name="Test Gateway 1",
            duid="test_duid",
            organization_id=uuid4(),
            location_id=uuid4(),
            gateway_id=uuid4()
        )
    )
    gateways = gateways_service.get_gateways_by_location_id(uuid4())
    assert gateways == []


def test_filter_by_returns_correct_gateways(gateways_service: GatewaysService):
    location_id = uuid4()
    gateways_service.create_gateway(GatewayCreate(
        name="Test Gateway 1",
        duid="test_duid1",
        organization_id=uuid4(),
        location_id=uuid4(),
        gateway_id=uuid4()
    ))
    gateway_create = GatewayCreate(
        name="Test Gateway 2",
        duid="test_duid2",
        organization_id=uuid4(),
        location_id=location_id,
        gateway_id=uuid4()
    )
    gateway = gateways_service.create_gateway(gateway_create)
    gateways = gateways_service.filter_by(location_id=location_id)
    assert gateways == [gateway]


def test_delete_gateway_removes_gateway_from_db(gateways_service: GatewaysService):
    gateway_create = GatewayCreate(
        name="Test Gateway",
        duid="test_duid",
        organization_id=uuid4(),
        location_id=uuid4(),
        gateway_id=uuid4()
    )
    gateway = gateways_service.create_gateway(gateway_create)
    gateways_service.delete_gateway(gateway.gateway_id)
    gateway_model = gateways_service.get_gateway_by_gateway_id(gateway.gateway_id)
    assert gateway_model is None
