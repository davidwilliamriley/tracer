from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from schemas.base import AuditSchema


class NodePropertyValueBase(BaseModel):
    node_id_fk: UUID
    node_property_definition_id_fk: UUID
    node_property_value: Optional[str] = None


class NodePropertyValueCreate(NodePropertyValueBase):
    created_by: Optional[str] = None


class NodePropertyValueUpdate(BaseModel):
    node_property_value: Optional[str] = None
    modified_by: Optional[str] = None


class NodePropertyValueResponse(NodePropertyValueBase, AuditSchema):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
