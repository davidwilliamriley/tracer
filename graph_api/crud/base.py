from typing import Any, Generic, List, Optional, Type, TypeVar
from uuid import UUID
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Generic CRUD base class.
    Each table-specific crud file instantiates this with its own types,
    then adds any custom query methods on top.

    Usage:
        class CRUDNodeType(CRUDBase[NodeType, NodeTypeCreate, NodeTypeUpdate]):
            ...  # add custom methods here
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: UUID) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == str(id)).first()

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_data = obj_in.model_dump()
        # Convert any UUID fields to strings for SQLite compatibility
        obj_data = {
            k: str(v) if isinstance(v, UUID) else v
            for k, v in obj_data.items()
        }
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        update_data = obj_in.model_dump(exclude_unset=True)
        update_data = {
            k: str(v) if isinstance(v, UUID) else v
            for k, v in update_data.items()
        }
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: UUID) -> Optional[ModelType]:
        obj = db.query(self.model).filter(self.model.id == str(id)).first()
        if not obj:
            return None
        db.delete(obj)
        db.commit()
        return obj
