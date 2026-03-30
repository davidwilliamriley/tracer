from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.node import Node
from schemas.node import NodeCreate, NodeUpdate
from crud.base import CRUDBase


class CRUDNode(CRUDBase[Node, NodeCreate, NodeUpdate]):

    def get_by_identifier(self, db: Session, identifier: str) -> Optional[Node]:
        return db.query(Node).filter(Node.node_identifier == identifier).first()

    def get_by_node_type(self, db: Session, node_type_id: UUID) -> List[Node]:
        """Return all nodes of a given NodeType."""
        return (
            db.query(Node)
            .filter(Node.node_type_id_fk == str(node_type_id))
            .all()
        )

    def search(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
        node_type_identifier: Optional[str] = None,
        name_contains: Optional[str] = None,
        identifier_contains: Optional[str] = None,
    ) -> tuple:
        """
        Dynamic filtered query on nodes.
        Filters are ANDed together — only provided filters are applied.
        Returns (items, total) for pagination.
        """
        from models.node_type import NodeType
        query = db.query(Node).join(NodeType, Node.node_type_id_fk == NodeType.id)

        if node_type_identifier:
            query = query.filter(
                NodeType.node_type_identifier == node_type_identifier
            )
        if name_contains:
            query = query.filter(
                Node.node_name.ilike(f"%{name_contains}%")
            )
        if identifier_contains:
            query = query.filter(
                Node.node_identifier.ilike(f"%{identifier_contains}%")
            )

        total = query.count()
        items = query.offset(skip).limit(limit).all()
        return items, total


node = CRUDNode(Node)
