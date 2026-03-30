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

    def search(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        edge_type_identifier: Optional[str] = None,
        name_contains: Optional[str] = None,
        source_node_id: Optional[UUID] = None,
        target_node_id: Optional[UUID] = None,
    ) -> tuple:
        """
        Dynamic filtered query on edges.
        Filters are ANDed together — only provided filters are applied.
        Returns (items, total) for pagination.
        """
        from models.edge_type import EdgeType
        query = db.query(Edge).join(EdgeType, Edge.edge_type_id_fk == EdgeType.id)

        if edge_type_identifier:
            query = query.filter(
                EdgeType.edge_type_identifier == edge_type_identifier
            )
        if name_contains:
            query = query.filter(
                Edge.edge_name.ilike(f"%{name_contains}%")
            )
        if source_node_id:
            query = query.filter(
                Edge.source_node_id_fk == str(source_node_id)
            )
        if target_node_id:
            query = query.filter(
                Edge.target_node_id_fk == str(target_node_id)
            )

        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total


edge = CRUDEdge(Edge)
