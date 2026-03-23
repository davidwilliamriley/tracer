from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


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


class NodeTypeResponse(NodeTypeBase):
    id: UUID                          # UUID not int
    created_by: Optional[str] = None
    created_on: Optional[datetime] = None
    modified_by: Optional[str] = None
    modified_on: Optional[datetime] = None

    class Config:
        from_attributes = True