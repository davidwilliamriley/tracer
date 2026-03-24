from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from schemas.node_property_value import (
    NodePropertyValueCreate,
    NodePropertyValueUpdate,
    NodePropertyValueResponse,
)
import crud

router = APIRouter(prefix="/node-property-values", tags=["Node Property Values"])


@router.get("/", response_model=List[NodePropertyValueResponse])
def list_node_property_values(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.node_property_value.get_multi(db, skip=skip, limit=limit)


@router.get("/by-node/{node_id}", response_model=List[NodePropertyValueResponse])
def list_values_by_node(node_id: UUID, db: Session = Depends(get_db)):
    """Return all property values for a given node."""
    if not crud.node.get(db, node_id):
        raise HTTPException(status_code=404, detail="Node not found")
    return crud.node_property_value.get_by_node(db, node_id)


@router.get("/{value_id}", response_model=NodePropertyValueResponse)
def get_node_property_value(value_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_property_value.get(db, value_id)
    if not obj:
        raise HTTPException(status_code=404, detail="NodePropertyValue not found")
    return obj


@router.post("/", response_model=NodePropertyValueResponse, status_code=201)
def create_or_update_node_property_value(
    payload: NodePropertyValueCreate, db: Session = Depends(get_db)
):
    """Create a property value, or update it if one already exists for this node+definition pair.
    This upsert behaviour matches the natural workflow of saving a node form."""
    if not crud.node.get(db, payload.node_id_fk):
        raise HTTPException(status_code=404, detail="Node not found")
    if not crud.node_property_definition.get(db, payload.node_property_definition_id_fk):
        raise HTTPException(status_code=404, detail="NodePropertyDefinition not found")
    return crud.node_property_value.upsert(db, obj_in=payload)


@router.put("/{value_id}", response_model=NodePropertyValueResponse)
def update_node_property_value(
    value_id: UUID, payload: NodePropertyValueUpdate, db: Session = Depends(get_db)
):
    obj = crud.node_property_value.get(db, value_id)
    if not obj:
        raise HTTPException(status_code=404, detail="NodePropertyValue not found")
    return crud.node_property_value.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{value_id}", response_model=NodePropertyValueResponse)
def delete_node_property_value(value_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_property_value.get(db, value_id)
    if not obj:
        raise HTTPException(status_code=404, detail="NodePropertyValue not found")
    return crud.node_property_value.remove(db, id=value_id)
