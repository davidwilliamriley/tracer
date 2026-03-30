import uuid
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db import Base
from models.base import GUID, AuditMixin


class NodePropertyValue(Base, AuditMixin):
    __tablename__ = "node_property_value"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    node_id_fk = Column(
        GUID, ForeignKey("node.id", ondelete="CASCADE"), nullable=False, index=True
    )
    node_property_definition_id_fk = Column(
        GUID,
        ForeignKey("node_property_definition.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    # All values stored as string; cast on read using the definition's type field
    node_property_value = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "node_id_fk",
            "node_property_definition_id_fk",
            name="uq_node_property_value"
        ),
    )

    node = relationship("Node", back_populates="property_values")
    node_property_definition = relationship(
        "NodePropertyDefinition", back_populates="property_values"
    )
