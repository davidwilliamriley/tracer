from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime


# ---------------------------------------------------------------------------
# Property value with its definition metadata attached
# Used inside NodeFull and EdgeFull so the frontend has everything in one hit
# ---------------------------------------------------------------------------

class PropertyValueDetail(BaseModel):
    """A single property value with its definition metadata."""
    value_id: UUID
    definition_id: UUID
    identifier: str
    name: str
    description: Optional[str]
    type: str                        # "string" | "integer" | "float" | "boolean" | "date"
    value: Optional[str]             # raw stored value (always string, cast on client)
    is_required: bool
    sort_order: int

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Node with all property values — the compound read for the node editor
# ---------------------------------------------------------------------------

class NodeFull(BaseModel):
    """
    A node with its type metadata and all property values resolved.
    Returned by GET /nodes/{id}/full.
    The frontend can render the node editor form directly from this response.
    """
    id: UUID
    node_identifier: str
    node_name: str
    node_type_id: UUID
    node_type_identifier: str
    node_type_name: str
    properties: List[PropertyValueDetail]
    created_by: Optional[str]
    created_on: Optional[datetime]
    modified_by: Optional[str]
    modified_on: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Edge with all property values — the compound read for the edge editor
# ---------------------------------------------------------------------------

class EdgeFull(BaseModel):
    """
    An edge with its type metadata, source/target node names,
    and all property values resolved.
    Returned by GET /edges/{id}/full.
    """
    id: UUID
    edge_identifier: str
    edge_name: str
    edge_type_id: UUID
    edge_type_identifier: str
    edge_type_name: str
    source_node_id: UUID
    source_node_identifier: str
    source_node_name: str
    target_node_id: UUID
    target_node_identifier: str
    target_node_name: str
    properties: List[PropertyValueDetail]
    created_by: Optional[str]
    created_on: Optional[datetime]
    modified_by: Optional[str]
    modified_on: Optional[datetime]

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Form schema — what the frontend calls to build a dynamic editor form
# ---------------------------------------------------------------------------

class FormField(BaseModel):
    """
    A single field in a dynamic editor form.
    The frontend uses this to decide what input to render and how to validate it.
    """
    assignment_id: UUID
    definition_id: UUID
    identifier: str
    name: str
    description: Optional[str]
    type: str                        # "string" | "integer" | "float" | "boolean" | "date"
    is_required: bool
    default_value: Optional[str]     # type-level default (overrides definition default)
    sort_order: int


class FormSchema(BaseModel):
    """
    The complete schema for a node or edge editor form.
    Returned by GET /node-types/{id}/form-schema
                and GET /edge-types/{id}/form-schema.
    """
    type_id: UUID
    type_identifier: str
    type_name: str
    fields: List[FormField]          # ordered by sort_order


# ---------------------------------------------------------------------------
# Bulk property write — saves all property values for a node/edge in one call
# ---------------------------------------------------------------------------

class PropertyValueInput(BaseModel):
    """One property value in a bulk write request."""
    definition_id: UUID
    value: Optional[str] = None


class BulkPropertyWrite(BaseModel):
    """
    Body for POST /nodes/{id}/properties and POST /edges/{id}/properties.
    Replaces the need to make N individual property value API calls when saving a form.
    """
    properties: List[PropertyValueInput]
    modified_by: Optional[str] = None


# ---------------------------------------------------------------------------
# Graph topology — what the canvas needs to render the full graph
# ---------------------------------------------------------------------------

class GraphNode(BaseModel):
    """A node in canvas-ready format."""
    id: UUID
    identifier: str
    name: str
    type_id: UUID
    type_identifier: str
    type_name: str


class GraphEdge(BaseModel):
    """An edge in canvas-ready format."""
    id: UUID
    identifier: str
    name: str
    type_id: UUID
    type_identifier: str
    type_name: str
    source: UUID                     # source node id
    target: UUID                     # target node id


class GraphTopology(BaseModel):
    """
    Complete graph topology for the canvas.
    Returned by GET /graph.
    Directly consumable by Cytoscape.js and react-flow.
    """
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    node_count: int
    edge_count: int
