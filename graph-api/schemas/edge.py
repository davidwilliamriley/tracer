from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from schemas.base import AuditSchema


class EdgeBase(BaseModel):
    edge_type_id_fk: UUID
    edge_identifier: str
    edge_name: str
    source_node_id_fk: UUID
    target_node_id_fk: UUID


class EdgeCreate(EdgeBase):
    created_by: Optional[str] = None


class EdgeUpdate(BaseModel):
    edge_name: Optional[str] = None
    modified_by: Optional[str] = None


class EdgeResponse(EdgeBase, AuditSchema):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
