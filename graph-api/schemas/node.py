from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from schemas.base import AuditSchema


class NodeBase(BaseModel):
    node_type_id_fk: UUID
    node_identifier: str
    node_name: str


class NodeCreate(NodeBase):
    created_by: Optional[str] = None


class NodeUpdate(BaseModel):
    node_name: Optional[str] = None
    modified_by: Optional[str] = None


class NodeResponse(NodeBase, AuditSchema):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
