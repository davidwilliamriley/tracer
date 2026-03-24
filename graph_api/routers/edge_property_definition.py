from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from schemas.edge_property_definition import (
    EdgePropertyDefinitionCreate,
    EdgePropertyDefinitionUpdate,
    EdgePropertyDefinitionResponse,
)
from schemas.node_property_definition import VALID_PROPERTY_TYPES
import crud

router = APIRouter(prefix="/edge-property-definitions", tags=["Edge Property Definitions"])


@router.get("/", response_model=List[EdgePropertyDefinitionResponse])
def list_edge_property_definitions(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.edge_property_definition.get_multi(db, skip=skip, limit=limit)


@router.get("/{definition_id}", response_model=EdgePropertyDefinitionResponse)
def get_edge_property_definition(definition_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge_property_definition.get(db, definition_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EdgePropertyDefinition not found")
    return obj


@router.post("/", response_model=EdgePropertyDefinitionResponse, status_code=201)
def create_edge_property_definition(
    payload: EdgePropertyDefinitionCreate, db: Session = Depends(get_db)
):
    if payload.edge_property_definition_type not in VALID_PROPERTY_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type. Must be one of: {sorted(VALID_PROPERTY_TYPES)}"
        )
    if crud.edge_property_definition.get_by_identifier(
        db, payload.edge_property_definition_identifier
    ):
        raise HTTPException(status_code=400, detail="Identifier already exists")
    return crud.edge_property_definition.create(db, obj_in=payload)


@router.put("/{definition_id}", response_model=EdgePropertyDefinitionResponse)
def update_edge_property_definition(
    definition_id: UUID,
    payload: EdgePropertyDefinitionUpdate,
    db: Session = Depends(get_db),
):
    obj = crud.edge_property_definition.get(db, definition_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EdgePropertyDefinition not found")
    if (
        payload.edge_property_definition_type
        and payload.edge_property_definition_type not in VALID_PROPERTY_TYPES
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type. Must be one of: {sorted(VALID_PROPERTY_TYPES)}"
        )
    return crud.edge_property_definition.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{definition_id}", response_model=EdgePropertyDefinitionResponse)
def delete_edge_property_definition(
    definition_id: UUID, db: Session = Depends(get_db)
):
    obj = crud.edge_property_definition.get(db, definition_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EdgePropertyDefinition not found")
    if obj.type_assignments:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot delete: this definition is assigned to "
                f"{len(obj.type_assignments)} edge type(s)"
            )
        )
    return crud.edge_property_definition.remove(db, id=definition_id)
