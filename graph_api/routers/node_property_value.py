from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from schemas.node_property_value import (
    NodePropertyValueCreate,
    NodePropertyValueUpdate,
    NodePropertyValueResponse,
)
from schemas.pagination import Page, PaginationParams
from exceptions import NotFoundError
from services.validation_service import validate_property_value
import crud

router = APIRouter(prefix="/node-property-values", tags=["Node Property Values"])


@router.get("/", response_model=Page[NodePropertyValueResponse])
def list_node_property_values(
    params: PaginationParams = Depends(), db: Session = Depends(get_db)
):
    items, total = crud.node_property_value.get_page(
        db, skip=params.skip, limit=params.limit
    )
    return Page.create(items, total, params)


@router.get("/by-node/{node_id}", response_model=List[NodePropertyValueResponse])
def list_values_by_node(node_id: UUID, db: Session = Depends(get_db)):
    if not crud.node.get(db, node_id):
        raise NotFoundError("Node", node_id)
    return crud.node_property_value.get_by_node(db, node_id)


@router.get("/{value_id}", response_model=NodePropertyValueResponse)
def get_node_property_value(value_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_property_value.get(db, value_id)
    if not obj:
        raise NotFoundError("NodePropertyValue", value_id)
    return obj


@router.post("/", response_model=NodePropertyValueResponse, status_code=201)
def create_or_update_node_property_value(
    payload: NodePropertyValueCreate, db: Session = Depends(get_db)
):
    """Create or update a property value (upsert by node + definition pair)."""
    if not crud.node.get(db, payload.node_id_fk):
        raise NotFoundError("Node", payload.node_id_fk)
    defn = crud.node_property_definition.get(db, payload.node_property_definition_id_fk)
    if not defn:
        raise NotFoundError("NodePropertyDefinition", payload.node_property_definition_id_fk)
    validate_property_value(
        value=payload.node_property_value,
        declared_type=defn.node_property_definition_type,
        field_name=defn.node_property_definition_identifier,
    )
    return crud.node_property_value.upsert(db, obj_in=payload)


@router.put("/{value_id}", response_model=NodePropertyValueResponse)
def update_node_property_value(
    value_id: UUID, payload: NodePropertyValueUpdate, db: Session = Depends(get_db)
):
    obj = crud.node_property_value.get(db, value_id)
    if not obj:
        raise NotFoundError("NodePropertyValue", value_id)
    return crud.node_property_value.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{value_id}", response_model=NodePropertyValueResponse)
def delete_node_property_value(value_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_property_value.get(db, value_id)
    if not obj:
        raise NotFoundError("NodePropertyValue", value_id)
    return crud.node_property_value.remove(db, id=value_id)
