from typing import List, Optional
from uuid import UUID

from app.v1.mesh_network.repositories.nodes_repository import NodesRepository
from app.v1.mesh_network.schemas.node import Node, NodeCreate


class NodesService:

    def __init__(self, nodes_repository: NodesRepository):
        self.nodes_repository = nodes_repository
    
    def create_node(self, node_create: NodeCreate) -> Node:
        return self.nodes_repository.create(node_create)

    def get_node_by_node_id(self, node_id: UUID) -> Optional[Node]:
        return self.nodes_repository.get(node_id)

    def get_nodes_by_gateway_id(self, gateway_id: UUID) -> List[Node]:
        return self.nodes_repository.filter_by(gateway_id=gateway_id)
    
    def get_node_for_gateway_by_node_id(self, gateway_id: UUID, node_id: UUID) -> Optional[Node]:
        nodes = self.nodes_repository.filter_by(gateway_id=gateway_id, node_id=node_id)
        if len(nodes) == 0:
            return None
        if len(nodes) > 1:
            raise ValueError("Multiple nodes with the same node_id and gateway_id")
        return nodes[0]
    
    def filter_by(self, **kwargs) -> List[Node]:
        return self.nodes_repository.filter_by(**kwargs)

    def delete_node(self, node_id: UUID) -> None:
        self.nodes_repository.delete(node_id)
