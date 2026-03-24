from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.edge_type_property_assignment import EdgeTypePropertyAssignment
from schemas.edge_type_property_assignment import (
    EdgeTypePropertyAssignmentCreate,
    EdgeTypePropertyAssignmentUpdate,
)
from crud.base import CRUDBase


class CRUDEdgeTypePropertyAssignment(
    CRUDBase[
        EdgeTypePropertyAssignment,
        EdgeTypePropertyAssignmentCreate,
        EdgeTypePropertyAssignmentUpdate,
    ]
):
    def get_by_edge_type(
        self, db: Session, edge_type_id: UUID
    ) -> List[EdgeTypePropertyAssignment]:
        """Return all property assignments for a given EdgeType, ordered by sort_order."""
        return (
            db.query(EdgeTypePropertyAssignment)
            .filter(EdgeTypePropertyAssignment.edge_type_id_fk == str(edge_type_id))
            .order_by(EdgeTypePropertyAssignment.sort_order)
            .all()
        )

    def get_existing(
        self,
        db: Session,
        edge_type_id: UUID,
        edge_property_definition_id: UUID,
    ) -> Optional[EdgeTypePropertyAssignment]:
        """Check if an assignment already exists (enforces unique constraint at app level)."""
        return (
            db.query(EdgeTypePropertyAssignment)
            .filter(
                EdgeTypePropertyAssignment.edge_type_id_fk == str(edge_type_id),
                EdgeTypePropertyAssignment.edge_property_definition_id_fk
                == str(edge_property_definition_id),
            )
            .first()
        )


edge_type_property_assignment = CRUDEdgeTypePropertyAssignment(
    EdgeTypePropertyAssignment
)
