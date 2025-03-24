from datetime import datetime, timezone
from uuid import uuid4, UUID

from app.v1.mesh_network.schemas.node import NodeTypeEnum
from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Node(Base):
    __tablename__ = 'nodes'

    node_id: Mapped[UUID] = mapped_column(primary_key=True, default=lambda: uuid4())
    name: Mapped[str] = mapped_column()
    duid: Mapped[str] = mapped_column(unique=True)
    type: Mapped[NodeTypeEnum] = mapped_column(String)
    gateway_id: Mapped[UUID] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(tz=timezone.utc), onupdate=lambda: datetime.now(tz=timezone.utc))

    __table_args__ = (UniqueConstraint('gateway_id', 'name', name='_nodes_unique_table_constraint'), )