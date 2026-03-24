from typing import List, Optional
from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from exceptions import NotFoundError, ValidationError
from models.node import Node
from models.edge import Edge
from models.node_type_property_assignment import NodeTypePropertyAssignment
from models.edge_type_property_assignment import EdgeTypePropertyAssignment
from models.node_property_value import NodePropertyValue
from models.edge_property_value import EdgePropertyValue
from models.node_property_definition import NodePropertyDefinition
from models.edge_property_definition import EdgePropertyDefinition
from schemas.graph import (
    NodeFull,
    EdgeFull,
    FormSchema,
    FormField,
    PropertyValueDetail,
    GraphTopology,
    GraphNode,
    GraphEdge,
    BulkPropertyWrite,
)
import crud


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _build_property_detail(
    assignment,
    definition,
    value_obj: Optional[NodePropertyValue | EdgePropertyValue],
) -> PropertyValueDetail:
    """
    Merge an assignment, its definition, and an optional value row
    into a single PropertyValueDetail for compound responses.
    """
    return PropertyValueDetail(
        value_id=value_obj.id if value_obj else uuid4(),  # placeholder if no value yet
        definition_id=definition.id,
        identifier=_node_or_edge_definition_identifier(definition),
        name=_node_or_edge_definition_name(definition),
        description=_node_or_edge_definition_description(definition),
        type=_node_or_edge_definition_type(definition),
        value=_node_or_edge_value(value_obj),
        is_required=assignment.is_required,
        sort_order=assignment.sort_order,
    )


def _node_or_edge_definition_identifier(definition) -> str:
    if hasattr(definition, "node_property_definition_identifier"):
        return definition.node_property_definition_identifier
    return definition.edge_property_definition_identifier


def _node_or_edge_definition_name(definition) -> str:
    if hasattr(definition, "node_property_definition_name"):
        return definition.node_property_definition_name
    return definition.edge_property_definition_name


def _node_or_edge_definition_description(definition) -> Optional[str]:
    if hasattr(definition, "node_property_definition_description"):
        return definition.node_property_definition_description
    return definition.edge_property_definition_description


def _node_or_edge_definition_type(definition) -> str:
    if hasattr(definition, "node_property_definition_type"):
        return definition.node_property_definition_type
    return definition.edge_property_definition_type


def _node_or_edge_value(value_obj) -> Optional[str]:
    if value_obj is None:
        return None
    if hasattr(value_obj, "node_property_value"):
        return value_obj.node_property_value
    return value_obj.edge_property_value


# ---------------------------------------------------------------------------
# NodeFull — node + type metadata + all property values
# ---------------------------------------------------------------------------

def get_node_full(db: Session, node_id: UUID) -> NodeFull:
    """
    Fetch a node with its type and all property values in one call.
    Walks the NodeType -> assignments -> definitions -> values chain.
    """
    node = crud.node.get(db, node_id)
    if not node:
        raise NotFoundError("Node", node_id)

    node_type = node.node_type

    # All assignments for this node's type, ordered by sort_order
    assignments = (
        db.query(NodeTypePropertyAssignment)
        .filter(NodeTypePropertyAssignment.node_type_id_fk == str(node_type.id))
        .order_by(NodeTypePropertyAssignment.sort_order)
        .all()
    )

    # All existing property values for this node, keyed by definition id
    existing_values = {
        str(v.node_property_definition_id_fk): v
        for v in db.query(NodePropertyValue)
        .filter(NodePropertyValue.node_id_fk == str(node_id))
        .all()
    }

    properties = []
    for assignment in assignments:
        definition = db.query(NodePropertyDefinition).filter(
            NodePropertyDefinition.id == assignment.node_property_definition_id_fk
        ).first()
        value_obj = existing_values.get(str(assignment.node_property_definition_id_fk))
        properties.append(_build_property_detail(assignment, definition, value_obj))

    return NodeFull(
        id=node.id,
        node_identifier=node.node_identifier,
        node_name=node.node_name,
        node_type_id=node_type.id,
        node_type_identifier=node_type.node_type_identifier,
        node_type_name=node_type.node_type_name,
        properties=properties,
        created_by=node.created_by,
        created_on=node.created_on,
        modified_by=node.modified_by,
        modified_on=node.modified_on,
    )


# ---------------------------------------------------------------------------
# EdgeFull — edge + type metadata + source/target names + all property values
# ---------------------------------------------------------------------------

def get_edge_full(db: Session, edge_id: UUID) -> EdgeFull:
    """
    Fetch an edge with its type, source/target node names,
    and all property values in one call.
    """
    edge = crud.edge.get(db, edge_id)
    if not edge:
        raise NotFoundError("Edge", edge_id)

    edge_type = edge.edge_type
    source = edge.source_node
    target = edge.target_node

    assignments = (
        db.query(EdgeTypePropertyAssignment)
        .filter(EdgeTypePropertyAssignment.edge_type_id_fk == str(edge_type.id))
        .order_by(EdgeTypePropertyAssignment.sort_order)
        .all()
    )

    existing_values = {
        str(v.edge_property_definition_id_fk): v
        for v in db.query(EdgePropertyValue)
        .filter(EdgePropertyValue.edge_id_fk == str(edge_id))
        .all()
    }

    properties = []
    for assignment in assignments:
        definition = db.query(EdgePropertyDefinition).filter(
            EdgePropertyDefinition.id == assignment.edge_property_definition_id_fk
        ).first()
        value_obj = existing_values.get(str(assignment.edge_property_definition_id_fk))
        properties.append(_build_property_detail(assignment, definition, value_obj))

    return EdgeFull(
        id=edge.id,
        edge_identifier=edge.edge_identifier,
        edge_name=edge.edge_name,
        edge_type_id=edge_type.id,
        edge_type_identifier=edge_type.edge_type_identifier,
        edge_type_name=edge_type.edge_type_name,
        source_node_id=source.id,
        source_node_identifier=source.node_identifier,
        source_node_name=source.node_name,
        target_node_id=target.id,
        target_node_identifier=target.node_identifier,
        target_node_name=target.node_name,
        properties=properties,
        created_by=edge.created_by,
        created_on=edge.created_on,
        modified_by=edge.modified_by,
        modified_on=edge.modified_on,
    )


# ---------------------------------------------------------------------------
# Form schema — ordered field list for building dynamic editor forms
# ---------------------------------------------------------------------------

def get_node_type_form_schema(db: Session, node_type_id: UUID) -> FormSchema:
    """
    Return the ordered field schema for a NodeType.
    The frontend calls this to know which fields to render in the node editor,
    what type each field is, and which are required.
    """
    node_type = crud.node_type.get(db, node_type_id)
    if not node_type:
        raise NotFoundError("NodeType", node_type_id)

    assignments = (
        db.query(NodeTypePropertyAssignment)
        .filter(NodeTypePropertyAssignment.node_type_id_fk == str(node_type_id))
        .order_by(NodeTypePropertyAssignment.sort_order)
        .all()
    )

    fields = []
    for assignment in assignments:
        definition = db.query(NodePropertyDefinition).filter(
            NodePropertyDefinition.id == assignment.node_property_definition_id_fk
        ).first()
        if not definition:
            continue

        # Assignment default_value overrides definition default_value
        effective_default = (
            assignment.default_value
            if assignment.default_value is not None
            else definition.node_property_definition_default_value
        )

        fields.append(FormField(
            assignment_id=assignment.id,
            definition_id=definition.id,
            identifier=definition.node_property_definition_identifier,
            name=definition.node_property_definition_name,
            description=definition.node_property_definition_description,
            type=definition.node_property_definition_type,
            is_required=assignment.is_required,
            default_value=effective_default,
            sort_order=assignment.sort_order,
        ))

    return FormSchema(
        type_id=node_type.id,
        type_identifier=node_type.node_type_identifier,
        type_name=node_type.node_type_name,
        fields=fields,
    )


def get_edge_type_form_schema(db: Session, edge_type_id: UUID) -> FormSchema:
    """
    Return the ordered field schema for an EdgeType.
    """
    edge_type = crud.edge_type.get(db, edge_type_id)
    if not edge_type:
        raise NotFoundError("EdgeType", edge_type_id)

    assignments = (
        db.query(EdgeTypePropertyAssignment)
        .filter(EdgeTypePropertyAssignment.edge_type_id_fk == str(edge_type_id))
        .order_by(EdgeTypePropertyAssignment.sort_order)
        .all()
    )

    fields = []
    for assignment in assignments:
        definition = db.query(EdgePropertyDefinition).filter(
            EdgePropertyDefinition.id == assignment.edge_property_definition_id_fk
        ).first()
        if not definition:
            continue

        effective_default = (
            assignment.default_value
            if assignment.default_value is not None
            else definition.edge_property_definition_default_value
        )

        fields.append(FormField(
            assignment_id=assignment.id,
            definition_id=definition.id,
            identifier=definition.edge_property_definition_identifier,
            name=definition.edge_property_definition_name,
            description=definition.edge_property_definition_description,
            type=definition.edge_property_definition_type,
            is_required=assignment.is_required,
            default_value=effective_default,
            sort_order=assignment.sort_order,
        ))

    return FormSchema(
        type_id=edge_type.id,
        type_identifier=edge_type.edge_type_identifier,
        type_name=edge_type.edge_type_name,
        fields=fields,
    )


# ---------------------------------------------------------------------------
# Bulk property write — upsert all property values for a node/edge at once
# ---------------------------------------------------------------------------

def bulk_write_node_properties(
    db: Session,
    node_id: UUID,
    payload: BulkPropertyWrite,
) -> NodeFull:
    """
    Upsert all property values for a node in a single transaction.
    Used when saving the node editor form — one call instead of N.
    Returns the full node so the frontend can update its state directly.
    """
    node = crud.node.get(db, node_id)
    if not node:
        raise NotFoundError("Node", node_id)

    # Validate all definition IDs exist before writing anything
    for item in payload.properties:
        if not crud.node_property_definition.get(db, item.definition_id):
            raise NotFoundError("NodePropertyDefinition", item.definition_id)

    # Upsert each value
    for item in payload.properties:
        existing = (
            db.query(NodePropertyValue)
            .filter(
                NodePropertyValue.node_id_fk == str(node_id),
                NodePropertyValue.node_property_definition_id_fk == str(item.definition_id),
            )
            .first()
        )
        if existing:
            existing.node_property_value = item.value
            if payload.modified_by:
                existing.modified_by = payload.modified_by
        else:
            db.add(NodePropertyValue(
                node_id_fk=str(node_id),
                node_property_definition_id_fk=str(item.definition_id),
                node_property_value=item.value,
                created_by=payload.modified_by,
            ))

    db.commit()
    return get_node_full(db, node_id)


def bulk_write_edge_properties(
    db: Session,
    edge_id: UUID,
    payload: BulkPropertyWrite,
) -> EdgeFull:
    """
    Upsert all property values for an edge in a single transaction.
    Returns the full edge so the frontend can update its state directly.
    """
    edge = crud.edge.get(db, edge_id)
    if not edge:
        raise NotFoundError("Edge", edge_id)

    for item in payload.properties:
        if not crud.edge_property_definition.get(db, item.definition_id):
            raise NotFoundError("EdgePropertyDefinition", item.definition_id)

    for item in payload.properties:
        existing = (
            db.query(EdgePropertyValue)
            .filter(
                EdgePropertyValue.edge_id_fk == str(edge_id),
                EdgePropertyValue.edge_property_definition_id_fk == str(item.definition_id),
            )
            .first()
        )
        if existing:
            existing.edge_property_value = item.value
            if payload.modified_by:
                existing.modified_by = payload.modified_by
        else:
            db.add(EdgePropertyValue(
                edge_id_fk=str(edge_id),
                edge_property_definition_id_fk=str(item.definition_id),
                edge_property_value=item.value,
                created_by=payload.modified_by,
            ))

    db.commit()
    return get_edge_full(db, edge_id)


# ---------------------------------------------------------------------------
# Graph topology — all nodes and edges for the canvas
# ---------------------------------------------------------------------------

def get_graph_topology(db: Session) -> GraphTopology:
    """
    Return all nodes and edges in canvas-ready format.
    Directly consumable by Cytoscape.js and react-flow without
    further transformation on the frontend.
    """
    nodes = db.query(Node).all()
    edges = db.query(Edge).all()

    graph_nodes = [
        GraphNode(
            id=n.id,
            identifier=n.node_identifier,
            name=n.node_name,
            type_id=n.node_type.id,
            type_identifier=n.node_type.node_type_identifier,
            type_name=n.node_type.node_type_name,
        )
        for n in nodes
    ]

    graph_edges = [
        GraphEdge(
            id=e.id,
            identifier=e.edge_identifier,
            name=e.edge_name,
            type_id=e.edge_type.id,
            type_identifier=e.edge_type.edge_type_identifier,
            type_name=e.edge_type.edge_type_name,
            source=e.source_node_id_fk,
            target=e.target_node_id_fk,
        )
        for e in edges
    ]

    return GraphTopology(
        nodes=graph_nodes,
        edges=graph_edges,
        node_count=len(graph_nodes),
        edge_count=len(graph_edges),
    )
