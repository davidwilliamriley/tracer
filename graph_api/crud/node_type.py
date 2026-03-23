from sqlalchemy.orm import Session
from models.node_type import NodeType
from schemas.node_type import NodeTypeCreate, NodeTypeUpdate


def get_node_type(db: Session, node_type_id: int):
    return db.query(NodeType).filter(NodeType.id == node_type_id).first()


def get_node_type_by_identifier(db: Session, identifier: str):
    return db.query(NodeType).filter(
        NodeType.node_type_identifier == identifier
    ).first()


def get_node_types(db: Session, skip: int = 0, limit: int = 100):
    return db.query(NodeType).offset(skip).limit(limit).all()


def create_node_type(db: Session, node_type: NodeTypeCreate):
    db_node_type = NodeType(**node_type.model_dump())
    db.add(db_node_type)
    db.commit()
    db.refresh(db_node_type)
    return db_node_type


def update_node_type(db: Session, node_type_id: int, updates: NodeTypeUpdate):
    db_node_type = get_node_type(db, node_type_id)
    if not db_node_type:
        return None
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_node_type, field, value)
    db.commit()
    db.refresh(db_node_type)
    return db_node_type


def delete_node_type(db: Session, node_type_id: int):
    db_node_type = get_node_type(db, node_type_id)
    if not db_node_type:
        return None
    db.delete(db_node_type)
    db.commit()
    return db_node_type