from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID
from database import get_db
from schemas.graph import (
    NodeFull,
    EdgeFull,
    FormSchema,
    BulkPropertyWrite,
    GraphTopology,
)
from services import graph_service

router = APIRouter(tags=["Graph"])


# ---------------------------------------------------------------------------
# Compound node read
# ---------------------------------------------------------------------------

@router.get("/nodes/{node_id}/full", response_model=NodeFull)
def get_node_full(node_id: UUID, db: Session = Depends(get_db)):
    """
    Return a node with its type metadata and all property values resolved.
    Use this endpoint to populate the node editor form — it replaces
    the three separate calls to /nodes/{id}, /node-property-values/by-node/{id},
    and /node-property-definitions/{id}.
    """
    return graph_service.get_node_full(db, node_id)


# ---------------------------------------------------------------------------
# Compound edge read
# ---------------------------------------------------------------------------

@router.get("/edges/{edge_id}/full", response_model=EdgeFull)
def get_edge_full(edge_id: UUID, db: Session = Depends(get_db)):
    """
    Return an edge with its type metadata, source/target node names,
    and all property values resolved.
    """
    return graph_service.get_edge_full(db, edge_id)


# ---------------------------------------------------------------------------
# Form schema endpoints
# ---------------------------------------------------------------------------

@router.get("/node-types/{node_type_id}/form-schema", response_model=FormSchema)
def get_node_type_form_schema(node_type_id: UUID, db: Session = Depends(get_db)):
    """
    Return the ordered field schema for a NodeType.

    Call this when the user selects a node type in the editor — the response
    tells the frontend exactly which fields to render, their types, which are
    required, and what the default values are. Fields are ordered by sort_order.

    Example response:
        {
          "type_id": "...",
          "type_identifier": "SAFETY_REQUIREMENT",
          "type_name": "Safety Requirement",
          "fields": [
            {
              "identifier": "REQ_ID",
              "name": "Requirement ID",
              "type": "string",
              "is_required": true,
              "default_value": null,
              "sort_order": 1
            },
            ...
          ]
        }
    """
    return graph_service.get_node_type_form_schema(db, node_type_id)


@router.get("/edge-types/{edge_type_id}/form-schema", response_model=FormSchema)
def get_edge_type_form_schema(edge_type_id: UUID, db: Session = Depends(get_db)):
    """
    Return the ordered field schema for an EdgeType.
    Same pattern as the node type form schema.
    """
    return graph_service.get_edge_type_form_schema(db, edge_type_id)


# ---------------------------------------------------------------------------
# Bulk property write
# ---------------------------------------------------------------------------

@router.post("/nodes/{node_id}/properties", response_model=NodeFull)
def bulk_write_node_properties(
    node_id: UUID,
    payload: BulkPropertyWrite,
    db: Session = Depends(get_db),
):
    """
    Upsert all property values for a node in a single request.

    Use this when saving the node editor form — send all property values
    at once rather than making one API call per field. All writes happen
    in a single transaction (all succeed or all fail).

    Returns the full node so the frontend can update its state directly
    without a follow-up GET.

    Example body:
        {
          "properties": [
            {"definition_id": "...", "value": "SR-001"},
            {"definition_id": "...", "value": "High"}
          ],
          "modified_by": "david"
        }
    """
    return graph_service.bulk_write_node_properties(db, node_id, payload)


@router.post("/edges/{edge_id}/properties", response_model=EdgeFull)
def bulk_write_edge_properties(
    edge_id: UUID,
    payload: BulkPropertyWrite,
    db: Session = Depends(get_db),
):
    """
    Upsert all property values for an edge in a single request.
    Same pattern as the node bulk write.
    """
    return graph_service.bulk_write_edge_properties(db, edge_id, payload)


# ---------------------------------------------------------------------------
# Graph topology
# ---------------------------------------------------------------------------

@router.get("/graph", response_model=GraphTopology)
def get_graph_topology(db: Session = Depends(get_db)):
    """
    Return all nodes and edges in canvas-ready format.

    Directly consumable by Cytoscape.js and react-flow.
    Node type information is embedded so the frontend can colour-code
    nodes by type without additional lookups.

    For large graphs (1000+ nodes) you will want to add filtering params
    here in Phase 2 — e.g. ?node_type=X or ?subgraph_root=Y.
    """
    return graph_service.get_graph_topology(db)
