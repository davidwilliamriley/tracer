import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from database import Base
from models.base import GUID, AuditMixin


class EdgePropertyDefinition(Base, AuditMixin):
    __tablename__ = "edge_property_definition"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    edge_property_definition_identifier = Column(
        String(255), unique=True, nullable=False, index=True
    )
    edge_property_definition_name = Column(String(255), nullable=False)
    edge_property_definition_description = Column(String, nullable=True)
    edge_property_definition_type = Column(
        String(50), nullable=False
    )  # e.g. "string", "integer", "float", "boolean", "date"
    edge_property_definition_default_value = Column(String, nullable=True)

    type_assignments = relationship(
        "EdgeTypePropertyAssignment",
        back_populates="edge_property_definition",
        cascade="all, delete-orphan"
    )
    property_values = relationship(
        "EdgePropertyValue",
        back_populates="edge_property_definition"
    )
