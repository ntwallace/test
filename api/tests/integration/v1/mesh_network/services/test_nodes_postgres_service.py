from uuid import uuid4, UUID

import pytest

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from app.v1.mesh_network.models.node import Node
from app.v1.mesh_network.repositories.nodes_repository import PostgresNodesRepository
from app.v1.mesh_network.schemas.node import NodeCreate
from app.v1.mesh_network.services.nodes import NodesService


def test_create_node_inserts_new_model(db_session_for_tests: Session):
    service = NodesService(
        nodes_repository=PostgresNodesRepository(db_session_for_tests)
    )
    node_create = NodeCreate(
        name="Test Node",
        duid="test_duid",
        type="standard",
        gateway_id=uuid4()
    )
    node = service.create_node(node_create)
    node_models = db_session_for_tests.query(Node).all()
    assert len(node_models) == 1
    node_model = node_models[0]
    assert node_model.node_id == node.node_id
    assert node_model.name == node.name
    assert node_model.duid == node.duid
    assert node_model.type == node.type
    assert node_model.gateway_id == node.gateway_id
    assert node_model.created_at == node.created_at
    assert node_model.updated_at == node.updated_at


def test_create_node_raises_error_if_node_exists(db_session_for_tests: Session):
    service = NodesService(
        nodes_repository=PostgresNodesRepository(db_session_for_tests)
    )
    node_create = NodeCreate(
        name="Test Node",
        duid="test_duid",
        type="standard",
        gateway_id=uuid4()
    )
    service.create_node(node_create)
    with pytest.raises(ValueError):
        service.create_node(node_create)


def test_get_node_by_id_returns_correct_node(db_session_for_tests: Session):
    service = NodesService(
        nodes_repository=PostgresNodesRepository(db_session_for_tests)
    )
    service.create_node(
        NodeCreate(
            name="Test Node 1",
            duid="test_duid1",
            type="standard",
            gateway_id=uuid4()
        )
    )
    node_create = NodeCreate(
        name="Test Node 2",
        duid="test_duid2",
        type="standard",
        gateway_id=uuid4()
    )
    node = service.create_node(node_create)
    node_model = service.get_node_by_node_id(node.node_id)
    assert node_model == node


def test_get_node_by_id_returns_none_if_node_not_found(db_session_for_tests: Session):
    service = NodesService(
        nodes_repository=PostgresNodesRepository(db_session_for_tests)
    )
    node_create = NodeCreate(
        name="Test Node",
        duid="test_duid",
        type="standard",
        gateway_id=uuid4()
    )
    service.create_node(node_create)
    node_model = service.get_node_by_node_id(uuid4())
    assert node_model is None


def test_get_nodes_by_gateway_id_returns_correct_nodes(db_session_for_tests: Session):
    service = NodesService(
        nodes_repository=PostgresNodesRepository(db_session_for_tests)
    )
    gateway_id = uuid4()
    service.create_node(
        NodeCreate(
            name="Test Node 1",
            duid="test_duid1",
            type="standard",
            gateway_id=uuid4()
        )
    )
    node_create = NodeCreate(
        name="Test Node 2",
        duid="test_duid2",
        type="standard",
        gateway_id=gateway_id
    )
    node = service.create_node(node_create)
    nodes = service.get_nodes_by_gateway_id(gateway_id)
    assert nodes == [node]


def test_get_nodes_by_gateway_id_returns_empty_list_if_no_nodes(db_session_for_tests: Session):
    service = NodesService(
        nodes_repository=PostgresNodesRepository(db_session_for_tests)
    )
    service.create_node(
        NodeCreate(
            name="Test Node 1",
            duid="test_duid",
            type="standard",
            gateway_id=uuid4()
        )
    )
    nodes = service.get_nodes_by_gateway_id(uuid4())
    assert nodes == []


def test_get_node_for_gateway_by_node_id_returns_correct_node(db_session_for_tests: Session):
    service = NodesService(
        nodes_repository=PostgresNodesRepository(db_session_for_tests)
    )
    gateway_id = uuid4()
    service.create_node(
        NodeCreate(
            name="Test Node 1",
            duid="test_duid1",
            type="standard",
            gateway_id=uuid4()
        )
    )
    node_create = NodeCreate(
        name="Test Node 2",
        duid="test_duid2",
        type="standard",
        gateway_id=gateway_id
    )
    node = service.create_node(node_create)
    node_model = service.get_node_for_gateway_by_node_id(gateway_id, node.node_id)
    assert node_model == node


def test_get_node_for_gateway_by_node_id_returns_none_if_node_not_found(db_session_for_tests: Session):
    service = NodesService(
        nodes_repository=PostgresNodesRepository(db_session_for_tests)
    )
    gateway_id = uuid4()
    node_create = NodeCreate(
        name="Test Node",
        duid="test_duid",
        type="standard",
        gateway_id=gateway_id
    )
    service.create_node(node_create)
    node_model = service.get_node_for_gateway_by_node_id(uuid4(), uuid4())
    assert node_model is None


def test_filter_by_returns_correct_nodes(db_session_for_tests: Session):
    service = NodesService(
        nodes_repository=PostgresNodesRepository(db_session_for_tests)
    )
    service.create_node(
        NodeCreate(
            name="Test Node 1",
            duid="test_duid1",
            type="standard",
            gateway_id=uuid4()
        )
    )
    node = service.create_node(
        NodeCreate(
            name="Test Node 2",
            duid="test_duid2",
            type="standard",
            gateway_id=uuid4()
        )
    )
    nodes = service.filter_by(name="Test Node 2")
    assert nodes == [node]


def test_delete_node_removes_node_from_db(db_session_for_tests: Session):
    service = NodesService(
        nodes_repository=PostgresNodesRepository(db_session_for_tests)
    )
    node_create = NodeCreate(
        name="Test Node",
        duid="test_duid",
        type="standard",
        gateway_id=uuid4()
    )
    node = service.create_node(node_create)
    service.delete_node(node.node_id)
    node_models = db_session_for_tests.query(Node).all()
    assert len(node_models) == 0
