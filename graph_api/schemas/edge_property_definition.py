from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from schemas.base import AuditSchema


class EdgePropertyDefinitionBase(BaseModel):
    edge_property_definition_identifier: str
    edge_property_definition_name: str
    edge_property_definition_description: Optional[str] = None
    edge_property_definition_type: str
    edge_property_definition_default_value: Optional[str] = None


class EdgePropertyDefinitionCreate(EdgePropertyDefinitionBase):
    created_by: Optional[str] = None


class EdgePropertyDefinitionUpdate(BaseModel):
    edge_property_definition_name: Optional[str] = None
    edge_property_definition_description: Optional[str] = None
    edge_property_definition_type: Optional[str] = None
    edge_property_definition_default_value: Optional[str] = None
    modified_by: Optional[str] = None


class EdgePropertyDefinitionResponse(EdgePropertyDefinitionBase, AuditSchema):
    id: UUID

    class Config:
        from_attributes = True
