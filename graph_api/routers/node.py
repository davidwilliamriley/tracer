from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from database import get_db
from schemas.node import NodeCreate, NodeUpdate, NodeResponse
from schemas.pagination import Page, PaginationParams
from exceptions import NotFoundError, ConflictError, DependencyError
import crud

router = APIRouter(prefix="/nodes", tags=["Nodes"])


@router.get("/", response_model=Page[NodeResponse])
def list_nodes(
    params: PaginationParams = Depends(),
    node_type_identifier: Optional[str] = Query(
        default=None,
        description="Filter by exact NodeType identifier e.g. SAFETY_REQUIREMENT"
    ),
    name_contains: Optional[str] = Query(
        default=None,
        description="Filter nodes whose name contains this string (case-insensitive)"
    ),
    identifier_contains: Optional[str] = Query(
        default=None,
        description="Filter nodes whose identifier contains this string (case-insensitive)"
    ),
    db: Session = Depends(get_db),
):
    if any([node_type_identifier, name_contains, identifier_contains]):
        items, total = crud.node.search(
            db,
            skip=params.skip,
            limit=params.limit,
            node_type_identifier=node_type_identifier,
            name_contains=name_contains,
            identifier_contains=identifier_contains,
        )
    else:
        items, total = crud.node.get_page(db, skip=params.skip, limit=params.limit)
    return Page.create(items, total, params)


@router.get("/by-type/{node_type_id}", response_model=List[NodeResponse])
def list_nodes_by_type(node_type_id: UUID, db: Session = Depends(get_db)):
    if not crud.node_type.get(db, node_type_id):
        raise NotFoundError("NodeType", node_type_id)
    return crud.node.get_by_node_type(db, node_type_id)


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(node_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node.get(db, node_id)
    if not obj:
        raise NotFoundError("Node", node_id)
    return obj


@router.post("/", response_model=NodeResponse, status_code=201)
def create_node(payload: NodeCreate, db: Session = Depends(get_db)):
    if not crud.node_type.get(db, payload.node_type_id_fk):
        raise NotFoundError("NodeType", payload.node_type_id_fk)
    if crud.node.get_by_identifier(db, payload.node_identifier):
        raise ConflictError(
            f"Node with identifier '{payload.node_identifier}' already exists",
            field="node_identifier",
        )
    return crud.node.create(db, obj_in=payload)


@router.put("/{node_id}", response_model=NodeResponse)
def update_node(node_id: UUID, payload: NodeUpdate, db: Session = Depends(get_db)):
    obj = crud.node.get(db, node_id)
    if not obj:
        raise NotFoundError("Node", node_id)
    return crud.node.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{node_id}", response_model=NodeResponse)
def delete_node(node_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node.get(db, node_id)
    if not obj:
        raise NotFoundError("Node", node_id)
    edge_count = len(obj.outgoing_edges) + len(obj.incoming_edges)
    if edge_count > 0:
        raise DependencyError(
            f"Cannot delete: node has {edge_count} connected edge(s). "
            "Delete connected edges first."
        )
    return crud.node.remove(db, id=node_id)
