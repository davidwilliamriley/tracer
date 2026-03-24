from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from schemas.node_property_definition import (
    NodePropertyDefinitionCreate,
    NodePropertyDefinitionUpdate,
    NodePropertyDefinitionResponse,
    VALID_PROPERTY_TYPES,
)
import crud

router = APIRouter(prefix="/node-property-definitions", tags=["Node Property Definitions"])


@router.get("/", response_model=List[NodePropertyDefinitionResponse])
def list_node_property_definitions(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.node_property_definition.get_multi(db, skip=skip, limit=limit)


@router.get("/{definition_id}", response_model=NodePropertyDefinitionResponse)
def get_node_property_definition(definition_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_property_definition.get(db, definition_id)
    if not obj:
        raise HTTPException(status_code=404, detail="NodePropertyDefinition not found")
    return obj


@router.post("/", response_model=NodePropertyDefinitionResponse, status_code=201)
def create_node_property_definition(
    payload: NodePropertyDefinitionCreate, db: Session = Depends(get_db)
):
    if payload.node_property_definition_type not in VALID_PROPERTY_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type. Must be one of: {sorted(VALID_PROPERTY_TYPES)}"
        )
    if crud.node_property_definition.get_by_identifier(
        db, payload.node_property_definition_identifier
    ):
        raise HTTPException(status_code=400, detail="Identifier already exists")
    return crud.node_property_definition.create(db, obj_in=payload)


@router.put("/{definition_id}", response_model=NodePropertyDefinitionResponse)
def update_node_property_definition(
    definition_id: UUID,
    payload: NodePropertyDefinitionUpdate,
    db: Session = Depends(get_db),
):
    obj = crud.node_property_definition.get(db, definition_id)
    if not obj:
        raise HTTPException(status_code=404, detail="NodePropertyDefinition not found")
    if (
        payload.node_property_definition_type
        and payload.node_property_definition_type not in VALID_PROPERTY_TYPES
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid type. Must be one of: {sorted(VALID_PROPERTY_TYPES)}"
        )
    return crud.node_property_definition.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{definition_id}", response_model=NodePropertyDefinitionResponse)
def delete_node_property_definition(
    definition_id: UUID, db: Session = Depends(get_db)
):
    obj = crud.node_property_definition.get(db, definition_id)
    if not obj:
        raise HTTPException(status_code=404, detail="NodePropertyDefinition not found")
    if obj.type_assignments:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot delete: this definition is assigned to "
                f"{len(obj.type_assignments)} node type(s)"
            )
        )
    return crud.node_property_definition.remove(db, id=definition_id)
