from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from database import get_db
from schemas.node import NodeCreate, NodeUpdate, NodeResponse
import crud

router = APIRouter(prefix="/nodes", tags=["Nodes"])


@router.get("/", response_model=List[NodeResponse])
def list_nodes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.node.get_multi(db, skip=skip, limit=limit)


@router.get("/by-type/{node_type_id}", response_model=List[NodeResponse])
def list_nodes_by_type(node_type_id: UUID, db: Session = Depends(get_db)):
    """Return all nodes of a given NodeType."""
    if not crud.node_type.get(db, node_type_id):
        raise HTTPException(status_code=404, detail="NodeType not found")
    return crud.node.get_by_node_type(db, node_type_id)


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(node_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node.get(db, node_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Node not found")
    return obj


@router.post("/", response_model=NodeResponse, status_code=201)
def create_node(payload: NodeCreate, db: Session = Depends(get_db)):
    if not crud.node_type.get(db, payload.node_type_id_fk):
        raise HTTPException(status_code=404, detail="NodeType not found")
    if crud.node.get_by_identifier(db, payload.node_identifier):
        raise HTTPException(status_code=400, detail="Node identifier already exists")
    return crud.node.create(db, obj_in=payload)


@router.put("/{node_id}", response_model=NodeResponse)
def update_node(node_id: UUID, payload: NodeUpdate, db: Session = Depends(get_db)):
    obj = crud.node.get(db, node_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Node not found")
    return crud.node.update(db, db_obj=obj, obj_in=payload)


@router.delete("/{node_id}", response_model=NodeResponse)
def delete_node(node_id: UUID, db: Session = Depends(get_db)):
    obj = crud.node.get(db, node_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Node not found")
    # Warn if node has edges — cascades will remove them
    edge_count = len(obj.outgoing_edges) + len(obj.incoming_edges)
    if edge_count > 0:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot delete: node has {edge_count} connected edge(s). "
                "Delete edges first or use force-delete."
            )
        )
    return crud.node.remove(db, id=node_id)
