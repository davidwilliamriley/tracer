from typing import Optional
from sqlalchemy.orm import Session
from models.edge_property_definition import EdgePropertyDefinition
from schemas.edge_property_definition import (
    EdgePropertyDefinitionCreate,
    EdgePropertyDefinitionUpdate,
)
from crud.base import CRUDBase


class CRUDEdgePropertyDefinition(
    CRUDBase[
        EdgePropertyDefinition,
        EdgePropertyDefinitionCreate,
        EdgePropertyDefinitionUpdate,
    ]
):
    def get_by_identifier(
        self, db: Session, identifier: str
    ) -> Optional[EdgePropertyDefinition]:
        return db.query(EdgePropertyDefinition).filter(
            EdgePropertyDefinition.edge_property_definition_identifier == identifier
        ).first()


edge_property_definition = CRUDEdgePropertyDefinition(EdgePropertyDefinition)
