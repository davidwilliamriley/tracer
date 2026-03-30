import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from db import Base
from models.base import GUID, AuditMixin


class NodePropertyDefinition(Base, AuditMixin):
    __tablename__ = "node_property_definition"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    node_property_definition_identifier = Column(
        String(255), unique=True, nullable=False, index=True
    )
    node_property_definition_name = Column(String(255), nullable=False)
    node_property_definition_description = Column(String, nullable=True)
    node_property_definition_type = Column(
        String(50), nullable=False
    )  # e.g. "string", "integer", "float", "boolean", "date"
    node_property_definition_default_value = Column(String, nullable=True)

    type_assignments = relationship(
        "NodeTypePropertyAssignment",
        back_populates="node_property_definition",
        cascade="all, delete-orphan"
    )
    property_values = relationship(
        "NodePropertyValue",
        back_populates="node_property_definition"
    )
