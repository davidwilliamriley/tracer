from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from schemas.base import AuditSchema


class EdgeTypeBase(BaseModel):
    edge_type_identifier: str
    edge_type_name: str
    edge_type_description: Optional[str] = None


class EdgeTypeCreate(EdgeTypeBase):
    created_by: Optional[str] = None


class EdgeTypeUpdate(BaseModel):
    edge_type_name: Optional[str] = None
    edge_type_description: Optional[str] = None
    modified_by: Optional[str] = None


class EdgeTypeResponse(EdgeTypeBase, AuditSchema):
    id: UUID

    class Config:
        from_attributes = True
