from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from db import get_db
from schemas.node_type_property_assignment import (
    NodeTypePropertyAssignmentCreate,
    NodeTypePropertyAssignmentUpdate,
    NodeTypePropertyAssignmentResponse,
)
from schemas.pagination import Page, PaginationParams
from exceptions import NotFoundError, ConflictError
import crud

router = APIRouter(
    prefix="/node-type-property-assignments",
    tags=["Node Type Property Assignments"],
)


@router.get("/", response_model=Page[NodeTypePropertyAssignmentResponse])
def list_assignments(
    params: PaginationParams = Depends(), db: Session = Depends(get_db)
):
    items, total = crud.node_type_property_assignment.get_page(
        db, skip=params.skip, limit=params.limit
    )
    return Page.create(items, total, params)


@router.get(
    "/by-node-type/{node_type_id}",
    response_model=List[NodeTypePropertyAssignmentResponse],
)
def list_assignments_by_node_type(node_type_id: UUID, db: Session = Depends(get_db)):
    """Return all property assignments for a NodeType ordered by sort_order.
    This is the key endpoint for building dynamic node editor forms."""
    if not crud.node_type.get(db, node_type_id):
        raise NotFoundError("NodeType", node_type_id)
    return crud.node_type_property_assignment.get_by_node_type(db, node_type_id)


@router.get("/{assignment_id}", response_model=NodeTypePropertyAssignmentResponse)
def get_assignment(assignment_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_type_property_assignment.get(db, assignment_id)
    if not obj:
        raise NotFoundError("NodeTypePropertyAssignment", assignment_id)
    return obj


@router.post("/", response_model=NodeTypePropertyAssignmentResponse, status_code=201)
def create_assignment(
    payload: NodeTypePropertyAssignmentCreate, db: Session = Depends(get_db)
):
    if not crud.node_type.get(db, payload.node_type_id_fk):
        raise NotFoundError("NodeType", payload.node_type_id_fk)
    if not crud.node_property_definition.get(db, payload.node_property_definition_id_fk):
        raise NotFoundError("NodePropertyDefinition", payload.node_property_definition_id_fk)
    if crud.node_type_property_assignment.get_existing(
        db,
        node_type_id=payload.node_type_id_fk,
        node_property_definition_id=payload.node_property_definition_id_fk,
    ):
        raise ConflictError("This property is already assigned to this node type")
    return crud.node_type_property_assignment.create(db, obj_in=payload)


@router.put("/{assignment_id}", response_model=NodeTypePropertyAssignmentResponse)
def update_assignment(
    assignment_id: UUID,
    payload: NodeTypePropertyAssignmentUpdate,
    db: Session = Depends(get_db),
):
    obj = crud.node_type_property_assignment.get(db, assignment_id)
    if not obj:
        raise NotFoundError("NodeTypePropertyAssignment", assignment_id)
    return crud.node_type_property_assignment.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{assignment_id}", response_model=NodeTypePropertyAssignmentResponse)
def delete_assignment(assignment_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_type_property_assignment.get(db, assignment_id)
    if not obj:
        raise NotFoundError("NodeTypePropertyAssignment", assignment_id)
    return crud.node_type_property_assignment.remove(db, id=assignment_id)
