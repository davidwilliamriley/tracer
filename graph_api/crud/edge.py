from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.edge import Edge
from schemas.edge import EdgeCreate, EdgeUpdate
from crud.base import CRUDBase


class CRUDEdge(CRUDBase[Edge, EdgeCreate, EdgeUpdate]):

    def get_by_identifier(self, db: Session, identifier: str) -> Optional[Edge]:
        return db.query(Edge).filter(Edge.edge_identifier == identifier).first()

    def get_by_edge_type(self, db: Session, edge_type_id: UUID) -> List[Edge]:
        """Return all edges of a given EdgeType."""
        return (
            db.query(Edge)
            .filter(Edge.edge_type_id_fk == str(edge_type_id))
            .all()
        )

    def get_by_source_node(self, db: Session, source_node_id: UUID) -> List[Edge]:
        """Return all edges leaving a given node."""
        return (
            db.query(Edge)
            .filter(Edge.source_node_id_fk == str(source_node_id))
            .all()
        )

    def get_by_target_node(self, db: Session, target_node_id: UUID) -> List[Edge]:
        """Return all edges arriving at a given node."""
        return (
            db.query(Edge)
            .filter(Edge.target_node_id_fk == str(target_node_id))
            .all()
        )


edge = CRUDEdge(Edge)
