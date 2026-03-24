from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from schemas.edge_type import EdgeTypeCreate, EdgeTypeUpdate, EdgeTypeResponse
import crud

router = APIRouter(prefix="/edge-types", tags=["Edge Types"])


@router.get("/", response_model=List[EdgeTypeResponse])
def list_edge_types(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.edge_type.get_multi(db, skip=skip, limit=limit)


@router.get("/{edge_type_id}", response_model=EdgeTypeResponse)
def get_edge_type(edge_type_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge_type.get(db, edge_type_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EdgeType not found")
    return obj


@router.post("/", response_model=EdgeTypeResponse, status_code=201)
def create_edge_type(payload: EdgeTypeCreate, db: Session = Depends(get_db)):
    if crud.edge_type.get_by_identifier(db, payload.edge_type_identifier):
        raise HTTPException(status_code=400, detail="Identifier already exists")
    return crud.edge_type.create(db, obj_in=payload)


@router.put("/{edge_type_id}", response_model=EdgeTypeResponse)
def update_edge_type(
    edge_type_id: UUID, payload: EdgeTypeUpdate, db: Session = Depends(get_db)
):
    obj = crud.edge_type.get(db, edge_type_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EdgeType not found")
    return crud.edge_type.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{edge_type_id}", response_model=EdgeTypeResponse)
def delete_edge_type(edge_type_id: UUID, db: Session = Depends(get_db)):
    obj = crud.edge_type.get(db, edge_type_id)
    if not obj:
        raise HTTPException(status_code=404, detail="EdgeType not found")
    if obj.edges:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete: {len(obj.edges)} edge(s) still use this type"
        )
    return crud.edge_type.remove(db, id=edge_type_id)
