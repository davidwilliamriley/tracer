import uuid
from sqlalchemy import Column, Boolean, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from models.base import GUID, AuditMixin


class NodeTypePropertyAssignment(Base, AuditMixin):
    __tablename__ = "node_type_property_assignment"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    node_type_id_fk = Column(
        GUID, ForeignKey("node_type.id", ondelete="CASCADE"), nullable=False, index=True
    )
    node_property_definition_id_fk = Column(
        GUID,
        ForeignKey("node_property_definition.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    is_required = Column(Boolean, default=False, nullable=False)
    default_value = Column(String, nullable=True)  # type-level override of definition default
    sort_order = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "node_type_id_fk",
            "node_property_definition_id_fk",
            name="uq_node_type_property"
        ),
    )

    node_type = relationship("NodeType", back_populates="property_assignments")
    node_property_definition = relationship(
        "NodePropertyDefinition", back_populates="type_assignments"
    )
