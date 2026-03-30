from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from db import get_db
from schemas.edge_type_property_assignment import (
    EdgeTypePropertyAssignmentCreate,
    EdgeTypePropertyAssignmentUpdate,
    EdgeTypePropertyAssignmentResponse,
)
from schemas.pagination import Page, PaginationParams
from exceptions import NotFoundError, ConflictError
import crud

router = APIRouter(
    prefix="/edge-type-property-assignments",
    tags=["Edge Type Property Assignments"],
)


@router.get("/", response_model=Page[EdgeTypePropertyAssignmentResponse])
def list_assignments(
    params: PaginationParams = Depends(), db: Session = Depends(get_db)
):
    items, total = crud.edge_type_property_assignment.get_page(
        db, skip=params.skip, limit=params.limit
    )
    return Page.create(items, total, params)


@router.get(
    "/by-edge-type/{edge_type_id}",
    response_model=List[EdgeTypePropertyAssignmentResponse],
)
def list_assignments_by_edge_type(edge_type_id: UUID, db: Session = Depends(get_db)):
    """Return all property assignments for an EdgeType ordered by sort_order."""
    if not crud.edge_type.get(db, edge_type_id):
        raise NotFoundError("EdgeType", edge_type_id)
    return crud.edge_type_property_assignment.get_by_edge_type(db, edge_type_id)


@router.get("/{assignment_id}", response_model=EdgeTypePropertyAssignmentResponse)
def get_assignment(assignment_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge_type_property_assignment.get(db, assignment_id)
    if not obj:
        raise NotFoundError("EdgeTypePropertyAssignment", assignment_id)
    return obj


@router.post("/", response_model=EdgeTypePropertyAssignmentResponse, status_code=201)
def create_assignment(
    payload: EdgeTypePropertyAssignmentCreate, db: Session = Depends(get_db)
):
    if not crud.edge_type.get(db, payload.edge_type_id_fk):
        raise NotFoundError("EdgeType", payload.edge_type_id_fk)
    if not crud.edge_property_definition.get(db, payload.edge_property_definition_id_fk):
        raise NotFoundError("EdgePropertyDefinition", payload.edge_property_definition_id_fk)
    if crud.edge_type_property_assignment.get_existing(
        db,
        edge_type_id=payload.edge_type_id_fk,
        edge_property_definition_id=payload.edge_property_definition_id_fk,
    ):
        raise ConflictError("This property is already assigned to this edge type")
    return crud.edge_type_property_assignment.create(db, obj_in=payload)


@router.put("/{assignment_id}", response_model=EdgeTypePropertyAssignmentResponse)
def update_assignment(
    assignment_id: UUID,
    payload: EdgeTypePropertyAssignmentUpdate,
    db: Session = Depends(get_db),
):
    obj = crud.edge_type_property_assignment.get(db, assignment_id)
    if not obj:
        raise NotFoundError("EdgeTypePropertyAssignment", assignment_id)
    return crud.edge_type_property_assignment.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{assignment_id}", response_model=EdgeTypePropertyAssignmentResponse)
def delete_assignment(assignment_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge_type_property_assignment.get(db, assignment_id)
    if not obj:
        raise NotFoundError("EdgeTypePropertyAssignment", assignment_id)
    return crud.edge_type_property_assignment.remove(db, id=assignment_id)
