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


node = CRUDNode(Node)
