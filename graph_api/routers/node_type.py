from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from schemas.node_type import NodeTypeCreate, NodeTypeUpdate, NodeTypeResponse
import crud

router = APIRouter(prefix="/node-types", tags=["Node Types"])


@router.get("/", response_model=List[NodeTypeResponse])
def list_node_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.node_type.get_multi(db, skip=skip, limit=limit)


@router.get("/{node_type_id}", response_model=NodeTypeResponse)
def get_node_type(node_type_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_type.get(db, node_type_id)
    if not obj:
        raise HTTPException(status_code=404, detail="NodeType not found")
    return obj


@router.post("/", response_model=NodeTypeResponse, status_code=201)
def create_node_type(payload: NodeTypeCreate, db: Session = Depends(get_db)):
    if crud.node_type.get_by_identifier(db, payload.node_type_identifier):
        raise HTTPException(status_code=400, detail="Identifier already exists")
    return crud.node_type.create(db, obj_in=payload)


@router.put("/{node_type_id}", response_model=NodeTypeResponse)
def update_node_type(
    node_type_id: UUID, payload: NodeTypeUpdate, db: Session = Depends(get_db)
):
    obj = crud.node_type.get(db, node_type_id)
    if not obj:
        raise HTTPException(status_code=404, detail="NodeType not found")
    return crud.node_type.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{node_type_id}", response_model=NodeTypeResponse)
def delete_node_type(node_type_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node_type.get(db, node_type_id)
    if not obj:
        raise HTTPException(status_code=404, detail="NodeType not found")
    if obj.nodes:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete: {len(obj.nodes)} node(s) still use this type"
        )
    return crud.node_type.remove(db, id=node_type_id)
