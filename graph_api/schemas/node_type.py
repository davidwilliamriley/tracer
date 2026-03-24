from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from schemas.base import AuditSchema


class NodeTypeBase(BaseModel):
    node_type_identifier: str
    node_type_name: str
    node_type_description: Optional[str] = None


class NodeTypeCreate(NodeTypeBase):
    created_by: Optional[str] = None


class NodeTypeUpdate(BaseModel):
    node_type_name: Optional[str] = None
    node_type_description: Optional[str] = None
    modified_by: Optional[str] = None


class NodeTypeResponse(NodeTypeBase, AuditSchema):
    id: UUID

    class Config:
        from_attributes = True
