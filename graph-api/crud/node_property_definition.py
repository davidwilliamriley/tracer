from typing import Optional
from sqlalchemy.orm import Session
from models.node_property_definition import NodePropertyDefinition
from schemas.node_property_definition import (
    NodePropertyDefinitionCreate,
    NodePropertyDefinitionUpdate,
)
from crud.base import CRUDBase


class CRUDNodePropertyDefinition(
    CRUDBase[
        NodePropertyDefinition,
        NodePropertyDefinitionCreate,
        NodePropertyDefinitionUpdate,
    ]
):
    def get_by_identifier(
        self, db: Session, identifier: str
    ) -> Optional[NodePropertyDefinition]:
        return db.query(NodePropertyDefinition).filter(
            NodePropertyDefinition.node_property_definition_identifier == identifier
        ).first()


node_property_definition = CRUDNodePropertyDefinition(NodePropertyDefinition)
