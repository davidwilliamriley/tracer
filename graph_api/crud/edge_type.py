from typing import Optional
from sqlalchemy.orm import Session
from models.edge_type import EdgeType
from schemas.edge_type import EdgeTypeCreate, EdgeTypeUpdate
from crud.base import CRUDBase


class CRUDEdgeType(CRUDBase[EdgeType, EdgeTypeCreate, EdgeTypeUpdate]):

    def get_by_identifier(self, db: Session, identifier: str) -> Optional[EdgeType]:
        return db.query(EdgeType).filter(
            EdgeType.edge_type_identifier == identifier
        ).first()


edge_type = CRUDEdgeType(EdgeType)
