from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from database import get_db
from schemas.node_type import NodeTypeCreate, NodeTypeUpdate, NodeTypeResponse
from schemas.pagination import Page, PaginationParams
from exceptions import NotFoundError, ConflictError, DependencyError
import crud

router = APIRouter(prefix="/node-types", tags=["Node Types"])


@router.get("/", response_model=Page[NodeTypeResponse])
def list_node_types(
    params: PaginationParams = Depends(), db: Session = Depends(get_db)
):
    items, total = crud.node_type.get_page(db, skip=params.skip, limit=params.limit)
    return Page.create(items, total, params)


@router.get("/{node_type_id}", response_model=NodeTypeResponse)
def get_node_type(node_type_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_type.get(db, node_type_id)
    if not obj:
        raise NotFoundError("NodeType", node_type_id)
    return obj


@router.post("/", response_model=NodeTypeResponse, status_code=201)
def create_node_type(payload: NodeTypeCreate, db: Session = Depends(get_db)):
    if crud.node_type.get_by_identifier(db, payload.node_type_identifier):
        raise ConflictError(
            f"NodeType with identifier '{payload.node_type_identifier}' already exists",
            field="node_type_identifier",
        )
    return crud.node_type.create(db, obj_in=payload)


@router.put("/{node_type_id}", response_model=NodeTypeResponse)
def update_node_type(
    node_type_id: UUID, payload: NodeTypeUpdate, db: Session = Depends(get_db)
):
    obj = crud.node_type.get(db, node_type_id)
    if not obj:
        raise NotFoundError("NodeType", node_type_id)
    return crud.node_type.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{node_type_id}", response_model=NodeTypeResponse)
def delete_node_type(node_type_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_type.get(db, node_type_id)
    if not obj:
        raise NotFoundError("NodeType", node_type_id)
    if obj.nodes:
        raise DependencyError(
            f"Cannot delete: {len(obj.nodes)} node(s) still use this type. "
            "Reassign or delete those nodes first."
        )
    return crud.node_type.remove(db, id=node_type_id)
