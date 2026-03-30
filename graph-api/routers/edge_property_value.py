from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from db import get_db
from schemas.edge_property_value import (
    EdgePropertyValueCreate,
    EdgePropertyValueUpdate,
    EdgePropertyValueResponse,
)
from schemas.pagination import Page, PaginationParams
from exceptions import NotFoundError
from services.validation_service import validate_property_value
import crud

router = APIRouter(prefix="/edge-property-values", tags=["Edge Property Values"])


@router.get("/", response_model=Page[EdgePropertyValueResponse])
def list_edge_property_values(
    params: PaginationParams = Depends(), db: Session = Depends(get_db)
):
    items, total = crud.edge_property_value.get_page(
        db, skip=params.skip, limit=params.limit
    )
    return Page.create(items, total, params)


@router.get("/by-edge/{edge_id}", response_model=List[EdgePropertyValueResponse])
def list_values_by_edge(edge_id: UUID, db: Session = Depends(get_db)):
    if not crud.edge.get(db, edge_id):
        raise NotFoundError("Edge", edge_id)
    return crud.edge_property_value.get_by_edge(db, edge_id)


@router.get("/{value_id}", response_model=EdgePropertyValueResponse)
def get_edge_property_value(value_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge_property_value.get(db, value_id)
    if not obj:
        raise NotFoundError("EdgePropertyValue", value_id)
    return obj


@router.post("/", response_model=EdgePropertyValueResponse, status_code=201)
def create_or_update_edge_property_value(
    payload: EdgePropertyValueCreate, db: Session = Depends(get_db)
):
    """Create or update a property value (upsert by edge + definition pair)."""
    if not crud.edge.get(db, payload.edge_id_fk):
        raise NotFoundError("Edge", payload.edge_id_fk)
    defn = crud.edge_property_definition.get(db, payload.edge_property_definition_id_fk)
    if not defn:
        raise NotFoundError("EdgePropertyDefinition", payload.edge_property_definition_id_fk)
    validate_property_value(
        value=payload.edge_property_value,
        declared_type=defn.edge_property_definition_type,
        field_name=defn.edge_property_definition_identifier,
    )
    return crud.edge_property_value.upsert(db, obj_in=payload)


@router.put("/{value_id}", response_model=EdgePropertyValueResponse)
def update_edge_property_value(
    value_id: UUID, payload: EdgePropertyValueUpdate, db: Session = Depends(get_db)
):
    obj = crud.edge_property_value.get(db, value_id)
    if not obj:
        raise NotFoundError("EdgePropertyValue", value_id)
    return crud.edge_property_value.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{value_id}", response_model=EdgePropertyValueResponse)
def delete_edge_property_value(value_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge_property_value.get(db, value_id)
    if not obj:
        raise NotFoundError("EdgePropertyValue", value_id)
    return crud.edge_property_value.remove(db, id=value_id)
