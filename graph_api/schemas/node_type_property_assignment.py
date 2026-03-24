from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from schemas.base import AuditSchema


class NodeTypePropertyAssignmentBase(BaseModel):
    node_type_id_fk: UUID
    node_property_definition_id_fk: UUID
    is_required: bool = False
    default_value: Optional[str] = None
    sort_order: int = 0


class NodeTypePropertyAssignmentCreate(NodeTypePropertyAssignmentBase):
    created_by: Optional[str] = None


class NodeTypePropertyAssignmentUpdate(BaseModel):
    is_required: Optional[bool] = None
    default_value: Optional[str] = None
    sort_order: Optional[int] = None
    modified_by: Optional[str] = None


class NodeTypePropertyAssignmentResponse(NodeTypePropertyAssignmentBase, AuditSchema):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
