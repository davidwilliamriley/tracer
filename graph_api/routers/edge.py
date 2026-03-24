from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from schemas.edge import EdgeCreate, EdgeUpdate, EdgeResponse
import crud

router = APIRouter(prefix="/edges", tags=["Edges"])


@router.get("/", response_model=List[EdgeResponse])
def list_edges(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.edge.get_multi(db, skip=skip, limit=limit)


@router.get("/by-type/{edge_type_id}", response_model=List[EdgeResponse])
def list_edges_by_type(edge_type_id: UUID, db: Session = Depends(get_db)):
    if not crud.edge_type.get(db, edge_type_id):
        raise HTTPException(status_code=404, detail="EdgeType not found")
    return crud.edge.get_by_edge_type(db, edge_type_id)


@router.get("/by-source/{node_id}", response_model=List[EdgeResponse])
def list_edges_by_source(node_id: UUID, db: Session = Depends(get_db)):
    """Return all edges leaving a given node."""
    if not crud.node.get(db, node_id):
        raise HTTPException(status_code=404, detail="Node not found")
    return crud.edge.get_by_source_node(db, node_id)


@router.get("/by-target/{node_id}", response_model=List[EdgeResponse])
def list_edges_by_target(node_id: UUID, db: Session = Depends(get_db)):
    """Return all edges arriving at a given node."""
    if not crud.node.get(db, node_id):
        raise HTTPException(status_code=404, detail="Node not found")
    return crud.edge.get_by_target_node(db, node_id)


@router.get("/{edge_id}", response_model=EdgeResponse)
def get_edge(edge_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge.get(db, edge_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Edge not found")
    return obj


@router.post("/", response_model=EdgeResponse, status_code=201)
def create_edge(payload: EdgeCreate, db: Session = Depends(get_db)):
    if not crud.edge_type.get(db, payload.edge_type_id_fk):
        raise HTTPException(status_code=404, detail="EdgeType not found")
    if not crud.node.get(db, payload.source_node_id_fk):
        raise HTTPException(status_code=404, detail="Source node not found")
    if not crud.node.get(db, payload.target_node_id_fk):
        raise HTTPException(status_code=404, detail="Target node not found")
    if crud.edge.get_by_identifier(db, payload.edge_identifier):
        raise HTTPException(status_code=400, detail="Edge identifier already exists")
    return crud.edge.create(db, obj_in=payload)


@router.put("/{edge_id}", response_model=EdgeResponse)
def update_edge(edge_id: UUID, payload: EdgeUpdate, db: Session = Depends(get_db)):
    obj = crud.edge.get(db, edge_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Edge not found")
    return crud.edge.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{edge_id}", response_model=EdgeResponse)
def delete_edge(edge_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge.get(db, edge_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Edge not found")
    return crud.edge.remove(db, id=edge_id)
