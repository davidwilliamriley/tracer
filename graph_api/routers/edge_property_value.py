from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from schemas.edge_property_value import (
    EdgePropertyValueCreate,
    EdgePropertyValueUpdate,
    EdgePropertyValueResponse,
)
import crud

router = APIRouter(prefix="/edge-property-values", tags=["Edge Property Values"])


@router.get("/", response_model=List[EdgePropertyValueResponse])
def list_edge_property_values(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.edge_property_value.get_multi(db, skip=skip, limit=limit)


@router.get("/by-edge/{edge_id}", response_model=List[EdgePropertyValueResponse])
def list_values_by_edge(edge_id: UUID, db: Session = Depends(get_db)):
    """Return all property values for a given edge."""
    if not crud.edge.get(db, edge_id):
        raise HTTPException(status_code=404, detail="Edge not found")
    return crud.edge_property_value.get_by_edge(db, edge_id)


@router.get("/{value_id}", response_model=EdgePropertyValueResponse)
def get_edge_property_value(value_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge_property_value.get(db, value_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EdgePropertyValue not found")
    return obj


@router.post("/", response_model=EdgePropertyValueResponse, status_code=201)
def create_or_update_edge_property_value(
    payload: EdgePropertyValueCreate, db: Session = Depends(get_db)
):
    """Create a property value, or update it if one already exists for this edge+definition pair."""
    if not crud.edge.get(db, payload.edge_id_fk):
        raise HTTPException(status_code=404, detail="Edge not found")
    if not crud.edge_property_definition.get(db, payload.edge_property_definition_id_fk):
        raise HTTPException(status_code=404, detail="EdgePropertyDefinition not found")
    return crud.edge_property_value.upsert(db, obj_in=payload)


@router.put("/{value_id}", response_model=EdgePropertyValueResponse)
def update_edge_property_value(
    value_id: UUID, payload: EdgePropertyValueUpdate, db: Session = Depends(get_db)
):
    obj = crud.edge_property_value.get(db, value_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EdgePropertyValue not found")
    return crud.edge_property_value.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{value_id}", response_model=EdgePropertyValueResponse)
def delete_edge_property_value(value_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge_property_value.get(db, value_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EdgePropertyValue not found")
    return crud.edge_property_value.remove(db, id=value_id)
