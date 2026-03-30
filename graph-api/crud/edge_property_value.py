from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.edge_property_value import EdgePropertyValue
from schemas.edge_property_value import EdgePropertyValueCreate, EdgePropertyValueUpdate
from crud.base import CRUDBase


class CRUDEdgePropertyValue(
    CRUDBase[EdgePropertyValue, EdgePropertyValueCreate, EdgePropertyValueUpdate]
):
    def get_by_edge(self, db: Session, edge_id: UUID) -> List[EdgePropertyValue]:
        """Return all property values for a given edge."""
        return (
            db.query(EdgePropertyValue)
            .filter(EdgePropertyValue.edge_id_fk == str(edge_id))
            .all()
        )

    def get_existing(
        self,
        db: Session,
        edge_id: UUID,
        edge_property_definition_id: UUID,
    ) -> Optional[EdgePropertyValue]:
        """Fetch a specific property value by edge + definition."""
        return (
            db.query(EdgePropertyValue)
            .filter(
                EdgePropertyValue.edge_id_fk == str(edge_id),
                EdgePropertyValue.edge_property_definition_id_fk
                == str(edge_property_definition_id),
            )
            .first()
        )

    def upsert(
        self,
        db: Session,
        *,
        obj_in: EdgePropertyValueCreate,
    ) -> EdgePropertyValue:
        """Create or update a property value for an edge+definition pair."""
        existing = self.get_existing(
            db,
            edge_id=obj_in.edge_id_fk,
            edge_property_definition_id=obj_in.edge_property_definition_id_fk,
        )
        if existing:
            from schemas.edge_property_value import EdgePropertyValueUpdate
            return self.update(
                db,
                db_obj=existing,
                obj_in=EdgePropertyValueUpdate(
                    edge_property_value=obj_in.edge_property_value,
                    modified_by=obj_in.created_by,
                ),
            )
        return self.create(db, obj_in=obj_in)


edge_property_value = CRUDEdgePropertyValue(EdgePropertyValue)
