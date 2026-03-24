import uuid
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from models.base import GUID, AuditMixin


class EdgePropertyValue(Base, AuditMixin):
    __tablename__ = "edge_property_value"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    edge_id_fk = Column(
        GUID, ForeignKey("edge.id", ondelete="CASCADE"), nullable=False, index=True
    )
    edge_property_definition_id_fk = Column(
        GUID,
        ForeignKey("edge_property_definition.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    edge_property_value = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint(
            "edge_id_fk",
            "edge_property_definition_id_fk",
            name="uq_edge_property_value"
        ),
    )

    edge = relationship("Edge", back_populates="property_values")
    edge_property_definition = relationship(
        "EdgePropertyDefinition", back_populates="property_values"
    )
