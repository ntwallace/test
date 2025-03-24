from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.v1.mesh_network.models.node import Node as NodeModel
from app.v1.mesh_network.schemas.node import NodeCreate, Node


class NodesRepository(ABC):

    @abstractmethod
    def create(self, node_create: NodeCreate) -> Node:
        ...
    
    @abstractmethod
    def get(self, node_id: UUID) -> Optional[Node]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[Node]:
        ...
    
    @abstractmethod
    def delete(self, node_id: UUID) -> None:
        ...


class PostgresNodesRepository(NodesRepository):

    def __init__(self, session: Session):
        self.session = session
    
    @final
    def create(self, node_create: NodeCreate) -> Node:
        try:
            node = NodeModel(
                name=node_create.name,
                duid=node_create.duid,
                gateway_id=node_create.gateway_id,
                type=node_create.type
            )
            self.session.add(node)
            self.session.commit()
            self.session.refresh(node)
            return Node.model_validate(node, from_attributes=True)
        except IntegrityError:
            raise ValueError

    @final
    def get(self, node_id: UUID) -> Optional[Node]:
        node = self.session.query(NodeModel).filter(NodeModel.node_id == node_id).first()
        if node is None:
            return None
        return Node.model_validate(node, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[Node]:
        nodes = self.session.query(NodeModel).filter_by(**kwargs).all()
        return [
            Node.model_validate(node, from_attributes=True)
            for node in nodes
        ]
    
    @final
    def delete(self, node_id: UUID) -> None:
        node = self.session.query(NodeModel).filter(NodeModel.node_id == node_id).first()
        if node:
            self.session.delete(node)
            self.session.commit()
