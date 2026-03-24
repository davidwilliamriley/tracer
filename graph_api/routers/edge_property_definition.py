from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from database import get_db
from schemas.edge_property_definition import (
    EdgePropertyDefinitionCreate,
    EdgePropertyDefinitionUpdate,
    EdgePropertyDefinitionResponse,
)
from schemas.node_property_definition import VALID_PROPERTY_TYPES
from schemas.pagination import Page, PaginationParams
from exceptions import NotFoundError, ConflictError, DependencyError, ValidationError
import crud

router = APIRouter(prefix="/edge-property-definitions", tags=["Edge Property Definitions"])


@router.get("/", response_model=Page[EdgePropertyDefinitionResponse])
def list_edge_property_definitions(
    params: PaginationParams = Depends(), db: Session = Depends(get_db)
):
    items, total = crud.edge_property_definition.get_page(
        db, skip=params.skip, limit=params.limit
    )
    return Page.create(items, total, params)


@router.get("/{definition_id}", response_model=EdgePropertyDefinitionResponse)
def get_edge_property_definition(definition_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge_property_definition.get(db, definition_id)
    if not obj:
        raise NotFoundError("EdgePropertyDefinition", definition_id)
    return obj


@router.post("/", response_model=EdgePropertyDefinitionResponse, status_code=201)
def create_edge_property_definition(
    payload: EdgePropertyDefinitionCreate, db: Session = Depends(get_db)
):
    if payload.edge_property_definition_type not in VALID_PROPERTY_TYPES:
        raise ValidationError(
            f"Invalid type '{payload.edge_property_definition_type}'. "
            f"Must be one of: {sorted(VALID_PROPERTY_TYPES)}",
            field="edge_property_definition_type",
        )
    if crud.edge_property_definition.get_by_identifier(
        db, payload.edge_property_definition_identifier
    ):
        raise ConflictError(
            f"EdgePropertyDefinition with identifier "
            f"'{payload.edge_property_definition_identifier}' already exists",
            field="edge_property_definition_identifier",
        )
    return crud.edge_property_definition.create(db, obj_in=payload)


@router.put("/{definition_id}", response_model=EdgePropertyDefinitionResponse)
def update_edge_property_definition(
    definition_id: UUID,
    payload: EdgePropertyDefinitionUpdate,
    db: Session = Depends(get_db),
):
    obj = crud.edge_property_definition.get(db, definition_id)
    if not obj:
        raise NotFoundError("EdgePropertyDefinition", definition_id)
    if (
        payload.edge_property_definition_type
        and payload.edge_property_definition_type not in VALID_PROPERTY_TYPES
    ):
        raise ValidationError(
            f"Invalid type '{payload.edge_property_definition_type}'. "
            f"Must be one of: {sorted(VALID_PROPERTY_TYPES)}",
            field="edge_property_definition_type",
        )
    return crud.edge_property_definition.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{definition_id}", response_model=EdgePropertyDefinitionResponse)
def delete_edge_property_definition(definition_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge_property_definition.get(db, definition_id)
    if not obj:
        raise NotFoundError("EdgePropertyDefinition", definition_id)
    if obj.type_assignments:
        raise DependencyError(
            f"Cannot delete: assigned to {len(obj.type_assignments)} edge type(s). "
            "Remove assignments first."
        )
    return crud.edge_property_definition.remove(db, id=definition_id)
