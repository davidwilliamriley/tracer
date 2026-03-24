from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.node_type_property_assignment import NodeTypePropertyAssignment
from schemas.node_type_property_assignment import (
    NodeTypePropertyAssignmentCreate,
    NodeTypePropertyAssignmentUpdate,
)
from crud.base import CRUDBase


class CRUDNodeTypePropertyAssignment(
    CRUDBase[
        NodeTypePropertyAssignment,
        NodeTypePropertyAssignmentCreate,
        NodeTypePropertyAssignmentUpdate,
    ]
):
    def get_by_node_type(
        self, db: Session, node_type_id: UUID
    ) -> List[NodeTypePropertyAssignment]:
        """Return all property assignments for a given NodeType, ordered by sort_order."""
        return (
            db.query(NodeTypePropertyAssignment)
            .filter(NodeTypePropertyAssignment.node_type_id_fk == str(node_type_id))
            .order_by(NodeTypePropertyAssignment.sort_order)
            .all()
        )

    def get_existing(
        self,
        db: Session,
        node_type_id: UUID,
        node_property_definition_id: UUID,
    ) -> Optional[NodeTypePropertyAssignment]:
        """Check if an assignment already exists (enforces unique constraint at app level)."""
        return (
            db.query(NodeTypePropertyAssignment)
            .filter(
                NodeTypePropertyAssignment.node_type_id_fk == str(node_type_id),
                NodeTypePropertyAssignment.node_property_definition_id_fk
                == str(node_property_definition_id),
            )
            .first()
        )


node_type_property_assignment = CRUDNodeTypePropertyAssignment(
    NodeTypePropertyAssignment
)
