import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from database import Base
from models.base import GUID, AuditMixin


class NodeType(Base, AuditMixin):
    __tablename__ = "node_type"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    node_type_identifier = Column(String(255), unique=True, nullable=False, index=True)
    node_type_name = Column(String(255), nullable=False)
    node_type_description = Column(String, nullable=True)

    property_assignments = relationship(
        "NodeTypePropertyAssignment",
        back_populates="node_type",
        cascade="all, delete-orphan"
    )
    nodes = relationship(
        "Node",
        back_populates="node_type"
    )
