import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from database import Base
from models.base import GUID, AuditMixin


class EdgeType(Base, AuditMixin):
    __tablename__ = "edge_type"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    edge_type_identifier = Column(String(255), unique=True, nullable=False, index=True)
    edge_type_name = Column(String(255), nullable=False)
    edge_type_description = Column(String, nullable=True)

    property_assignments = relationship(
        "EdgeTypePropertyAssignment",
        back_populates="edge_type",
        cascade="all, delete-orphan"
    )
    edges = relationship(
        "Edge",
        back_populates="edge_type"
    )
