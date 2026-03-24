from typing import Optional
from sqlalchemy.orm import Session
from models.node_type import NodeType
from schemas.node_type import NodeTypeCreate, NodeTypeUpdate
from crud.base import CRUDBase


class CRUDNodeType(CRUDBase[NodeType, NodeTypeCreate, NodeTypeUpdate]):

    def get_by_identifier(self, db: Session, identifier: str) -> Optional[NodeType]:
        return db.query(NodeType).filter(
            NodeType.node_type_identifier == identifier
        ).first()


node_type = CRUDNodeType(NodeType)
