from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from crud import node_type as crud
from schemas.node_type import NodeTypeCreate, NodeTypeUpdate, NodeTypeResponse
from typing import List

router = APIRouter(prefix="/node-types", tags=["Node Types"])


@router.get("/", response_model=List[NodeTypeResponse])
def list_node_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_node_types(db, skip=skip, limit=limit)


@router.get("/{node_type_id}", response_model=NodeTypeResponse)
def get_node_type(node_type_id: int, db: Session = Depends(get_db)):
    db_node_type = crud.get_node_type(db, node_type_id)
    if not db_node_type:
        raise HTTPException(status_code=404, detail="NodeType not found")
    return db_node_type


@router.post("/", response_model=NodeTypeResponse, status_code=201)
def create_node_type(node_type: NodeTypeCreate, db: Session = Depends(get_db)):
    existing = crud.get_node_type_by_identifier(db, node_type.node_type_identifier)
    if existing:
        raise HTTPException(status_code=400, detail="Identifier already exists")
    return crud.create_node_type(db, node_type)


@router.put("/{node_type_id}", response_model=NodeTypeResponse)
def update_node_type(
    node_type_id: int, updates: NodeTypeUpdate, db: Session = Depends(get_db)
):
    updated = crud.update_node_type(db, node_type_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail="NodeType not found")
    return updated


@router.delete("/{node_type_id}", response_model=NodeTypeResponse)
def delete_node_type(node_type_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_node_type(db, node_type_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="NodeType not found")
    return deleted