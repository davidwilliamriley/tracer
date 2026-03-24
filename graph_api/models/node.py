import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from models.base import GUID, AuditMixin


class Node(Base, AuditMixin):
    __tablename__ = "node"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    node_type_id_fk = Column(
        GUID, ForeignKey("node_type.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    node_identifier = Column(String(255), unique=True, nullable=False, index=True)
    node_name = Column(String(255), nullable=False)

    node_type = relationship("NodeType", back_populates="nodes")
    property_values = relationship(
        "NodePropertyValue",
        back_populates="node",
        cascade="all, delete-orphan"
    )
    # Edges where this node is the source
    outgoing_edges = relationship(
        "Edge",
        foreign_keys="Edge.source_node_id_fk",
        back_populates="source_node"
    )
    # Edges where this node is the target
    incoming_edges = relationship(
        "Edge",
        foreign_keys="Edge.target_node_id_fk",
        back_populates="target_node"
    )
