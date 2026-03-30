import uuid
from sqlalchemy import Column, Boolean, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db import Base
from models.base import GUID, AuditMixin


class EdgeTypePropertyAssignment(Base, AuditMixin):
    __tablename__ = "edge_type_property_assignment"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    edge_type_id_fk = Column(
        GUID, ForeignKey("edge_type.id", ondelete="CASCADE"), nullable=False, index=True
    )
    edge_property_definition_id_fk = Column(
        GUID,
        ForeignKey("edge_property_definition.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    is_required = Column(Boolean, default=False, nullable=False)
    default_value = Column(String, nullable=True)
    sort_order = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "edge_type_id_fk",
            "edge_property_definition_id_fk",
            name="uq_edge_type_property"
        ),
    )

    edge_type = relationship("EdgeType", back_populates="property_assignments")
    edge_property_definition = relationship(
        "EdgePropertyDefinition", back_populates="type_assignments"
    )
