from pydantic import BaseModel, ConfigDict
from typing import Optional
from uuid import UUID
from schemas.base import AuditSchema


class EdgePropertyValueBase(BaseModel):
    edge_id_fk: UUID
    edge_property_definition_id_fk: UUID
    edge_property_value: Optional[str] = None


class EdgePropertyValueCreate(EdgePropertyValueBase):
    created_by: Optional[str] = None


class EdgePropertyValueUpdate(BaseModel):
    edge_property_value: Optional[str] = None
    modified_by: Optional[str] = None


class EdgePropertyValueResponse(EdgePropertyValueBase, AuditSchema):
    id: UUID
    model_config = ConfigDict(from_attributes=True)
