from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel


class NodeTypeEnum(StrEnum):
    STANDARD = 'standard'
    MODBUS = 'modbus'


class NodeBase(BaseModel):
    name: str
    duid: str
    gateway_id: UUID
    type: NodeTypeEnum


class NodeCreate(NodeBase):
    pass


class Node(NodeBase):
    node_id: UUID
    created_at: datetime
    updated_at: datetime

    class ConfigDict:
        from_attributes = True
