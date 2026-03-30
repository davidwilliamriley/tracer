import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from db import Base
from models.base import GUID, AuditMixin


class Edge(Base, AuditMixin):
    __tablename__ = "edge"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    edge_type_id_fk = Column(
        GUID, ForeignKey("edge_type.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    edge_identifier = Column(String(255), unique=True, nullable=False, index=True)
    edge_name = Column(String(255), nullable=False)
    source_node_id_fk = Column(
        GUID, ForeignKey("node.id", ondelete="CASCADE"), nullable=False, index=True
    )
    target_node_id_fk = Column(
        GUID, ForeignKey("node.id", ondelete="CASCADE"), nullable=False, index=True
    )

    edge_type = relationship("EdgeType", back_populates="edges")
    source_node = relationship(
        "Node",
        foreign_keys=[source_node_id_fk],
        back_populates="outgoing_edges"
    )
    target_node = relationship(
        "Node",
        foreign_keys=[target_node_id_fk],
        back_populates="incoming_edges"
    )
    property_values = relationship(
        "EdgePropertyValue",
        back_populates="edge",
        cascade="all, delete-orphan"
    )
