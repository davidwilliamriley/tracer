from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from schemas.base import AuditSchema

VALID_PROPERTY_TYPES = {"string", "integer", "float", "boolean", "date"}


class NodePropertyDefinitionBase(BaseModel):
    node_property_definition_identifier: str
    node_property_definition_name: str
    node_property_definition_description: Optional[str] = None
    node_property_definition_type: (
        str  # validated in router against VALID_PROPERTY_TYPES
    )
    node_property_definition_default_value: Optional[str] = None


class NodePropertyDefinitionCreate(NodePropertyDefinitionBase):
    created_by: Optional[str] = None


class NodePropertyDefinitionUpdate(BaseModel):
    node_property_definition_name: Optional[str] = None
    node_property_definition_description: Optional[str] = None
    node_property_definition_type: Optional[str] = None
    node_property_definition_default_value: Optional[str] = None
    modified_by: Optional[str] = None


class NodePropertyDefinitionResponse(NodePropertyDefinitionBase, AuditSchema):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
