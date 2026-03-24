from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from database import get_db
from schemas.node_property_definition import (
    NodePropertyDefinitionCreate,
    NodePropertyDefinitionUpdate,
    NodePropertyDefinitionResponse,
    VALID_PROPERTY_TYPES,
)
from schemas.pagination import Page, PaginationParams
from exceptions import NotFoundError, ConflictError, DependencyError, ValidationError
import crud

router = APIRouter(prefix="/node-property-definitions", tags=["Node Property Definitions"])


@router.get("/", response_model=Page[NodePropertyDefinitionResponse])
def list_node_property_definitions(
    params: PaginationParams = Depends(), db: Session = Depends(get_db)
):
    items, total = crud.node_property_definition.get_page(
        db, skip=params.skip, limit=params.limit
    )
    return Page.create(items, total, params)


@router.get("/{definition_id}", response_model=NodePropertyDefinitionResponse)
def get_node_property_definition(definition_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_property_definition.get(db, definition_id)
    if not obj:
        raise NotFoundError("NodePropertyDefinition", definition_id)
    return obj


@router.post("/", response_model=NodePropertyDefinitionResponse, status_code=201)
def create_node_property_definition(
    payload: NodePropertyDefinitionCreate, db: Session = Depends(get_db)
):
    if payload.node_property_definition_type not in VALID_PROPERTY_TYPES:
        raise ValidationError(
            f"Invalid type '{payload.node_property_definition_type}'. "
            f"Must be one of: {sorted(VALID_PROPERTY_TYPES)}",
            field="node_property_definition_type",
        )
    if crud.node_property_definition.get_by_identifier(
        db, payload.node_property_definition_identifier
    ):
        raise ConflictError(
            f"NodePropertyDefinition with identifier "
            f"'{payload.node_property_definition_identifier}' already exists",
            field="node_property_definition_identifier",
        )
    return crud.node_property_definition.create(db, obj_in=payload)


@router.put("/{definition_id}", response_model=NodePropertyDefinitionResponse)
def update_node_property_definition(
    definition_id: UUID,
    payload: NodePropertyDefinitionUpdate,
    db: Session = Depends(get_db),
):
    obj = crud.node_property_definition.get(db, definition_id)
    if not obj:
        raise NotFoundError("NodePropertyDefinition", definition_id)
    if (
        payload.node_property_definition_type
        and payload.node_property_definition_type not in VALID_PROPERTY_TYPES
    ):
        raise ValidationError(
            f"Invalid type '{payload.node_property_definition_type}'. "
            f"Must be one of: {sorted(VALID_PROPERTY_TYPES)}",
            field="node_property_definition_type",
        )
    return crud.node_property_definition.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{definition_id}", response_model=NodePropertyDefinitionResponse)
def delete_node_property_definition(definition_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_property_definition.get(db, definition_id)
    if not obj:
        raise NotFoundError("NodePropertyDefinition", definition_id)
    if obj.type_assignments:
        raise DependencyError(
            f"Cannot delete: assigned to {len(obj.type_assignments)} node type(s). "
            "Remove assignments first."
        )
    return crud.node_property_definition.remove(db, id=definition_id)
