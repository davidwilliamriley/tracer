from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from schemas.node_type_property_assignment import (
    NodeTypePropertyAssignmentCreate,
    NodeTypePropertyAssignmentUpdate,
    NodeTypePropertyAssignmentResponse,
)
import crud

router = APIRouter(
    prefix="/node-type-property-assignments",
    tags=["Node Type Property Assignments"],
)


@router.get("/", response_model=List[NodeTypePropertyAssignmentResponse])
def list_assignments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.node_type_property_assignment.get_multi(db, skip=skip, limit=limit)


@router.get(
    "/by-node-type/{node_type_id}",
    response_model=List[NodeTypePropertyAssignmentResponse],
)
def list_assignments_by_node_type(
    node_type_id: UUID, db: Session = Depends(get_db)
):
    """Return all property assignments for a NodeType, ordered by sort_order.
    This is the key endpoint for building dynamic forms in the frontend."""
    if not crud.node_type.get(db, node_type_id):
        raise HTTPException(status_code=404, detail="NodeType not found")
    return crud.node_type_property_assignment.get_by_node_type(db, node_type_id)


@router.get("/{assignment_id}", response_model=NodeTypePropertyAssignmentResponse)
def get_assignment(assignment_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_type_property_assignment.get(db, assignment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return obj


@router.post("/", response_model=NodeTypePropertyAssignmentResponse, status_code=201)
def create_assignment(
    payload: NodeTypePropertyAssignmentCreate, db: Session = Depends(get_db)
):
    if not crud.node_type.get(db, payload.node_type_id_fk):
        raise HTTPException(status_code=404, detail="NodeType not found")
    if not crud.node_property_definition.get(db, payload.node_property_definition_id_fk):
        raise HTTPException(status_code=404, detail="NodePropertyDefinition not found")
    existing = crud.node_type_property_assignment.get_existing(
        db,
        node_type_id=payload.node_type_id_fk,
        node_property_definition_id=payload.node_property_definition_id_fk,
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="This property is already assigned to this node type"
        )
    return crud.node_type_property_assignment.create(db, obj_in=payload)


@router.put("/{assignment_id}", response_model=NodeTypePropertyAssignmentResponse)
def update_assignment(
    assignment_id: UUID,
    payload: NodeTypePropertyAssignmentUpdate,
    db: Session = Depends(get_db),
):
    obj = crud.node_type_property_assignment.get(db, assignment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return crud.node_type_property_assignment.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{assignment_id}", response_model=NodeTypePropertyAssignmentResponse)
def delete_assignment(assignment_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_type_property_assignment.get(db, assignment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return crud.node_type_property_assignment.remove(db, id=assignment_id)
