from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from db import get_db
from schemas.edge_type import EdgeTypeCreate, EdgeTypeUpdate, EdgeTypeResponse
from schemas.pagination import Page, PaginationParams
from exceptions import NotFoundError, ConflictError, DependencyError
import crud

router = APIRouter(prefix="/edge-types", tags=["Edge Types"])


@router.get("/", response_model=Page[EdgeTypeResponse])
def list_edge_types(
    params: PaginationParams = Depends(), db: Session = Depends(get_db)
):
    items, total = crud.edge_type.get_page(db, skip=params.skip, limit=params.limit)
    return Page.create(items, total, params)


@router.get("/{edge_type_id}", response_model=EdgeTypeResponse)
def get_edge_type(edge_type_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge_type.get(db, edge_type_id)
    if not obj:
        raise NotFoundError("EdgeType", edge_type_id)
    return obj


@router.post("/", response_model=EdgeTypeResponse, status_code=201)
def create_edge_type(payload: EdgeTypeCreate, db: Session = Depends(get_db)):
    if crud.edge_type.get_by_identifier(db, payload.edge_type_identifier):
        raise ConflictError(
            f"EdgeType with identifier '{payload.edge_type_identifier}' already exists",
            field="edge_type_identifier",
        )
    return crud.edge_type.create(db, obj_in=payload)


@router.put("/{edge_type_id}", response_model=EdgeTypeResponse)
def update_edge_type(
    edge_type_id: UUID, payload: EdgeTypeUpdate, db: Session = Depends(get_db)
):
    obj = crud.edge_type.get(db, edge_type_id)
    if not obj:
        raise NotFoundError("EdgeType", edge_type_id)
    return crud.edge_type.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{edge_type_id}", response_model=EdgeTypeResponse)
def delete_edge_type(edge_type_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge_type.get(db, edge_type_id)
    if not obj:
        raise NotFoundError("EdgeType", edge_type_id)
    if obj.edges:
        raise DependencyError(
            f"Cannot delete: {len(obj.edges)} edge(s) still use this type. "
            "Reassign or delete those edges first."
        )
    return crud.edge_type.remove(db, id=edge_type_id)
