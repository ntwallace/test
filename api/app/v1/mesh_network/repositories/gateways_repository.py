from abc import ABC, abstractmethod
from typing import List, Optional, final
from uuid import UUID

from sqlalchemy.orm import Session

from app.v1.mesh_network.models.gateway import Gateway as GatewayModel
from app.v1.mesh_network.schemas.gateway import Gateway, GatewayCreate


class GatewaysRepository(ABC):

    @abstractmethod
    def create(self, gateway_create: GatewayCreate) -> Gateway:
        ...
    
    @abstractmethod
    def get(self, gateway_id: UUID) -> Optional[Gateway]:
        ...
    
    @abstractmethod
    def get_by_duid(self, gateway_duid: str) -> Optional[Gateway]:
        ...
    
    @abstractmethod
    def filter_by(self, **kwargs) -> List[Gateway]:
        ...
    
    @abstractmethod
    def delete(self, gateway_id: UUID) -> None:
        ...


class PostgresGatewaysRepository(GatewaysRepository):

    def __init__(self, session: Session) -> None:
        self.session = session
    
    @final
    def create(self, gateway_create: GatewayCreate) -> Gateway:
        gateway = GatewayModel(
            name=gateway_create.name,
            duid=gateway_create.duid,
            location_id=gateway_create.location_id
        )
        self.session.add(gateway)
        self.session.commit()
        self.session.refresh(gateway)
        return Gateway.model_validate(gateway, from_attributes=True)

    @final
    def get(self, gateway_id: UUID) -> Optional[Gateway]:
        gateway = self.session.query(GatewayModel).filter(GatewayModel.gateway_id == gateway_id).first()
        if gateway is None:
            return None
        return Gateway.model_validate(gateway, from_attributes=True)
    
    @final
    def get_by_duid(self, gateway_duid: str) -> Optional[Gateway]:
        gateway = self.session.query(GatewayModel).filter(GatewayModel.duid == gateway_duid).first()
        if gateway is None:
            return None
        return Gateway.model_validate(gateway, from_attributes=True)
    
    @final
    def filter_by(self, **kwargs) -> List[Gateway]:
        gateways = self.session.query(GatewayModel).filter_by(**kwargs).all()
        return [
            Gateway.model_validate(gateway, from_attributes=True)
            for gateway in gateways
        ]
    
    @final
    def delete(self, gateway_id: UUID) -> None:
        gateway = self.session.query(GatewayModel).filter(GatewayModel.gateway_id == gateway_id).first()
        if gateway:
            self.session.delete(gateway)
            self.session.commit()
