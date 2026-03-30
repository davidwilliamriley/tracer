from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from models.node_property_value import NodePropertyValue
from schemas.node_property_value import NodePropertyValueCreate, NodePropertyValueUpdate
from crud.base import CRUDBase


class CRUDNodePropertyValue(
    CRUDBase[NodePropertyValue, NodePropertyValueCreate, NodePropertyValueUpdate]
):
    def get_by_node(self, db: Session, node_id: UUID) -> List[NodePropertyValue]:
        """Return all property values for a given node."""
        return (
            db.query(NodePropertyValue)
            .filter(NodePropertyValue.node_id_fk == str(node_id))
            .all()
        )

    def get_existing(
        self,
        db: Session,
        node_id: UUID,
        node_property_definition_id: UUID,
    ) -> Optional[NodePropertyValue]:
        """Fetch a specific property value by node + definition (enforces unique constraint)."""
        return (
            db.query(NodePropertyValue)
            .filter(
                NodePropertyValue.node_id_fk == str(node_id),
                NodePropertyValue.node_property_definition_id_fk
                == str(node_property_definition_id),
            )
            .first()
        )

    def upsert(
        self,
        db: Session,
        *,
        obj_in: NodePropertyValueCreate,
    ) -> NodePropertyValue:
        """Create or update a property value for a node+definition pair."""
        existing = self.get_existing(
            db,
            node_id=obj_in.node_id_fk,
            node_property_definition_id=obj_in.node_property_definition_id_fk,
        )
        if existing:
            from schemas.node_property_value import NodePropertyValueUpdate
            return self.update(
                db,
                db_obj=existing,
                obj_in=NodePropertyValueUpdate(
                    node_property_value=obj_in.node_property_value,
                    modified_by=obj_in.created_by,
                ),
            )
        return self.create(db, obj_in=obj_in)


node_property_value = CRUDNodePropertyValue(NodePropertyValue)
