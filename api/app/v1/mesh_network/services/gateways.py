from typing import List, Optional
from uuid import UUID

from app.v1.mesh_network.repositories.gateways_repository import GatewaysRepository
from app.v1.mesh_network.schemas.gateway import Gateway, GatewayCreate


class GatewaysService:

    def __init__(self, gateways_repository: GatewaysRepository) -> None:
        self.gateways_repository = gateways_repository
    
    def create_gateway(self, gateway_create: GatewayCreate) -> Gateway:
        return self.gateways_repository.create(gateway_create)

    def get_gateway_by_gateway_id(self, gateway_id: UUID) -> Optional[Gateway]:
        return self.gateways_repository.get(gateway_id)

    def get_gateway_by_duid(self, gateway_duid: str) -> Optional[Gateway]:
        return self.gateways_repository.get_by_duid(gateway_duid)

    def get_gateways_by_location_id(self, location_id: UUID) -> list[Gateway]:
        return self.gateways_repository.filter_by(location_id=location_id)

    def filter_by(self, **kwargs) -> List[Gateway]:
        return self.gateways_repository.filter_by(**kwargs)

    def delete_gateway(self, gateway_id: UUID) -> None:
        self.gateways_repository.delete(gateway_id)
