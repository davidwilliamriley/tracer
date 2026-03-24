from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from schemas.edge import EdgeCreate, EdgeUpdate, EdgeResponse
from schemas.pagination import Page, PaginationParams
from exceptions import NotFoundError, ConflictError
import crud

router = APIRouter(prefix="/edges", tags=["Edges"])


@router.get("/", response_model=Page[EdgeResponse])
def list_edges(params: PaginationParams = Depends(), db: Session = Depends(get_db)):
    items, total = crud.edge.get_page(db, skip=params.skip, limit=params.limit)
    return Page.create(items, total, params)


@router.get("/by-type/{edge_type_id}", response_model=List[EdgeResponse])
def list_edges_by_type(edge_type_id: UUID, db: Session = Depends(get_db)):
    if not crud.edge_type.get(db, edge_type_id):
        raise NotFoundError("EdgeType", edge_type_id)
    return crud.edge.get_by_edge_type(db, edge_type_id)


@router.get("/by-source/{node_id}", response_model=List[EdgeResponse])
def list_edges_by_source(node_id: UUID, db: Session = Depends(get_db)):
    if not crud.node.get(db, node_id):
        raise NotFoundError("Node", node_id)
    return crud.edge.get_by_source_node(db, node_id)


@router.get("/by-target/{node_id}", response_model=List[EdgeResponse])
def list_edges_by_target(node_id: UUID, db: Session = Depends(get_db)):
    if not crud.node.get(db, node_id):
        raise NotFoundError("Node", node_id)
    return crud.edge.get_by_target_node(db, node_id)


@router.get("/{edge_id}", response_model=EdgeResponse)
def get_edge(edge_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge.get(db, edge_id)
    if not obj:
        raise NotFoundError("Edge", edge_id)
    return obj


@router.post("/", response_model=EdgeResponse, status_code=201)
def create_edge(payload: EdgeCreate, db: Session = Depends(get_db)):
    if not crud.edge_type.get(db, payload.edge_type_id_fk):
        raise NotFoundError("EdgeType", payload.edge_type_id_fk)
    if not crud.node.get(db, payload.source_node_id_fk):
        raise NotFoundError("Source node", payload.source_node_id_fk)
    if not crud.node.get(db, payload.target_node_id_fk):
        raise NotFoundError("Target node", payload.target_node_id_fk)
    if crud.edge.get_by_identifier(db, payload.edge_identifier):
        raise ConflictError(
            f"Edge with identifier '{payload.edge_identifier}' already exists",
            field="edge_identifier",
        )
    return crud.edge.create(db, obj_in=payload)


@router.put("/{edge_id}", response_model=EdgeResponse)
def update_edge(edge_id: UUID, payload: EdgeUpdate, db: Session = Depends(get_db)):
    obj = crud.edge.get(db, edge_id)
    if not obj:
        raise NotFoundError("Edge", edge_id)
    return crud.edge.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{edge_id}", response_model=EdgeResponse)
def delete_edge(edge_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge.get(db, edge_id)
    if not obj:
        raise NotFoundError("Edge", edge_id)
    return crud.edge.remove(db, id=edge_id)
