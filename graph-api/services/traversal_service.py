"""
traversal_service.py

Graph traversal using NetworkX.

Architecture:
  - build_nx_graph() loads the full graph from SQLite into a NetworkX DiGraph
  - Each traversal function calls build_nx_graph(), runs its algorithm,
    then maps results back to API response schemas

Why rebuild the graph per request rather than caching?
  At Tracer's scale (hundreds to low thousands of nodes) this is fast enough
  (~5-20ms) and keeps the code simple. If the graph grows to tens of thousands
  of nodes, add a cache with invalidation on node/edge write. The service layer
  boundary means that change is isolated here.

Why DiGraph rather than Graph?
  Edges in Tracer are directed (source → target). DiGraph preserves direction,
  which matters for path finding and subgraph reachability. Neighbour queries
  expose both directions explicitly via the `direction` field.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
import networkx as nx

from exceptions import NotFoundError, ValidationError
from models.node import Node
from models.edge import Edge
from schemas.graph import (
    NeighbourEdge,
    NeighbourNode,
    NeighboursResponse,
    PathNode,
    PathEdge,
    PathResponse,
    SubgraphResponse,
    GraphNode,
    GraphEdge,
)


# ---------------------------------------------------------------------------
# Graph builder — SQLite → NetworkX DiGraph
# ---------------------------------------------------------------------------

def build_nx_graph(db: Session) -> tuple[nx.DiGraph, dict, dict]:
    """
    Load the full graph from SQLite into a NetworkX DiGraph.

    Returns:
        G:            The NetworkX DiGraph (nodes keyed by UUID string)
        node_data:    Dict mapping node_id_str → Node ORM object
        edge_data:    Dict mapping (source_id_str, target_id_str, edge_id_str)
                      → Edge ORM object, stored as edge key in a MultiDiGraph
                      style but accessible via G.edges data

    Node attributes stored on G:
        identifier, name, type_identifier, type_name, type_id

    Edge attributes stored on G:
        edge_id, identifier, name, edge_type_identifier, source_id, target_id
    """
    nodes = db.query(Node).all()
    edges = db.query(Edge).all()

    G = nx.DiGraph()
    node_data = {}
    edge_data = {}

    for n in nodes:
        node_id = str(n.id)
        G.add_node(
            node_id,
            identifier=n.node_identifier,
            name=n.node_name,
            type_id=str(n.node_type.id),
            type_identifier=n.node_type.node_type_identifier,
            type_name=n.node_type.node_type_name,
        )
        node_data[node_id] = n

    for e in edges:
        source_id = str(e.source_node_id_fk)
        target_id = str(e.target_node_id_fk)
        edge_id = str(e.id)
        G.add_edge(
            source_id,
            target_id,
            edge_id=edge_id,
            identifier=e.edge_identifier,
            name=e.edge_name,
            edge_type_identifier=e.edge_type.edge_type_identifier,
        )
        edge_data[edge_id] = e

    return G, node_data, edge_data


# ---------------------------------------------------------------------------
# Neighbours — one hop in either direction
# ---------------------------------------------------------------------------

def get_neighbours(db: Session, node_id: UUID) -> NeighboursResponse:
    """
    Return all nodes connected to node_id by exactly one edge,
    in either direction (outgoing or incoming).

    Each neighbour includes the edge(s) that connect it, labelled
    with direction so the frontend can render arrows correctly.
    """
    node = db.query(Node).filter(Node.id == str(node_id)).first()
    if not node:
        raise NotFoundError("Node", node_id)

    G, node_data, _ = build_nx_graph(db)
    node_id_str = str(node_id)

    # Collect neighbours with their connecting edges
    # Use a dict keyed by neighbour_id to merge multiple edges to the same node
    neighbour_map: dict[str, list[NeighbourEdge]] = {}

    # Outgoing edges (node → neighbour)
    for _, target_id, edge_attrs in G.out_edges(node_id_str, data=True):
        if target_id not in neighbour_map:
            neighbour_map[target_id] = []
        neighbour_map[target_id].append(NeighbourEdge(
            edge_id=UUID(edge_attrs["edge_id"]),
            edge_identifier=edge_attrs["identifier"],
            edge_name=edge_attrs["name"],
            edge_type_identifier=edge_attrs["edge_type_identifier"],
            direction="outgoing",
        ))

    # Incoming edges (neighbour → node)
    for source_id, _, edge_attrs in G.in_edges(node_id_str, data=True):
        if source_id not in neighbour_map:
            neighbour_map[source_id] = []
        neighbour_map[source_id].append(NeighbourEdge(
            edge_id=UUID(edge_attrs["edge_id"]),
            edge_identifier=edge_attrs["identifier"],
            edge_name=edge_attrs["name"],
            edge_type_identifier=edge_attrs["edge_type_identifier"],
            direction="incoming",
        ))

    neighbours = []
    for neighbour_id_str, edges in neighbour_map.items():
        n_attrs = G.nodes[neighbour_id_str]
        neighbours.append(NeighbourNode(
            id=UUID(neighbour_id_str),
            identifier=n_attrs["identifier"],
            name=n_attrs["name"],
            type_identifier=n_attrs["type_identifier"],
            type_name=n_attrs["type_name"],
            edges=edges,
        ))

    return NeighboursResponse(
        node_id=node_id,
        node_identifier=node.node_identifier,
        neighbour_count=len(neighbours),
        neighbours=neighbours,
    )


# ---------------------------------------------------------------------------
# Shortest path — directed path between two nodes
# ---------------------------------------------------------------------------

def get_shortest_path(
    db: Session,
    source_id: UUID,
    target_id: UUID,
) -> PathResponse:
    """
    Find the shortest directed path from source to target.

    Uses Dijkstra's algorithm (nx.shortest_path) on the DiGraph.
    All edges are treated as equal weight — shortest path = fewest hops.

    Returns a PathResponse with found=False if no path exists rather
    than raising an error, so the frontend can handle it gracefully.
    """
    source = db.query(Node).filter(Node.id == str(source_id)).first()
    if not source:
        raise NotFoundError("Source node", source_id)

    target = db.query(Node).filter(Node.id == str(target_id)).first()
    if not target:
        raise NotFoundError("Target node", target_id)

    if source_id == target_id:
        raise ValidationError("Source and target nodes must be different")

    G, node_data, _ = build_nx_graph(db)
    source_str = str(source_id)
    target_str = str(target_id)

    try:
        path_node_ids = nx.shortest_path(G, source=source_str, target=target_str)
    except nx.NetworkXNoPath:
        return PathResponse(
            source_id=source_id,
            target_id=target_id,
            found=False,
            hop_count=0,
            nodes=[],
            edges=[],
        )
    except nx.NodeNotFound:
        return PathResponse(
            source_id=source_id,
            target_id=target_id,
            found=False,
            hop_count=0,
            nodes=[],
            edges=[],
        )

    # Build path nodes
    path_nodes = []
    for nid in path_node_ids:
        attrs = G.nodes[nid]
        path_nodes.append(PathNode(
            id=UUID(nid),
            identifier=attrs["identifier"],
            name=attrs["name"],
            type_identifier=attrs["type_identifier"],
        ))

    # Build path edges (one per consecutive pair of nodes)
    path_edges = []
    for i in range(len(path_node_ids) - 1):
        src = path_node_ids[i]
        tgt = path_node_ids[i + 1]
        edge_attrs = G.edges[src, tgt]
        path_edges.append(PathEdge(
            id=UUID(edge_attrs["edge_id"]),
            identifier=edge_attrs["identifier"],
            edge_type_identifier=edge_attrs["edge_type_identifier"],
            source_id=UUID(src),
            target_id=UUID(tgt),
        ))

    return PathResponse(
        source_id=source_id,
        target_id=target_id,
        found=True,
        hop_count=len(path_edges),
        nodes=path_nodes,
        edges=path_edges,
    )


# ---------------------------------------------------------------------------
# Subgraph — all nodes reachable from a root
# ---------------------------------------------------------------------------

def get_subgraph(
    db: Session,
    root_id: UUID,
    max_depth: int = 5,
) -> SubgraphResponse:
    """
    Return all nodes reachable from root_id following directed edges,
    up to max_depth hops.

    Uses BFS (nx.single_source_shortest_path_length) to find reachable
    nodes within the depth limit, then extracts the induced subgraph.

    This is useful for rendering a focused subgraph on the canvas —
    e.g. "show me everything downstream of this hazard".

    Args:
        root_id:   Starting node
        max_depth: Maximum number of hops to follow (default 5, max 20)
    """
    if max_depth < 1 or max_depth > 20:
        raise ValidationError(
            "max_depth must be between 1 and 20",
            field="max_depth",
        )

    root = db.query(Node).filter(Node.id == str(root_id)).first()
    if not root:
        raise NotFoundError("Node", root_id)

    G, _, _ = build_nx_graph(db)
    root_str = str(root_id)

    # BFS from root — returns {node_id: depth}
    reachable = nx.single_source_shortest_path_length(G, root_str, cutoff=max_depth)

    # The induced subgraph contains only reachable nodes and edges between them
    subgraph = G.subgraph(reachable.keys())

    sub_nodes = []
    for nid in subgraph.nodes():
        attrs = G.nodes[nid]
        sub_nodes.append(GraphNode(
            id=UUID(nid),
            identifier=attrs["identifier"],
            name=attrs["name"],
            type_id=UUID(attrs["type_id"]),
            type_identifier=attrs["type_identifier"],
            type_name=attrs["type_name"],
        ))

    sub_edges = []
    for src, tgt, attrs in subgraph.edges(data=True):
        sub_edges.append(GraphEdge(
            id=UUID(attrs["edge_id"]),
            identifier=attrs["identifier"],
            name=attrs["name"],
            type_id=UUID(attrs["edge_id"]),  # placeholder — edge type id not on G
            type_identifier=attrs["edge_type_identifier"],
            type_name=attrs["edge_type_identifier"],  # name == identifier here
            source=UUID(src),
            target=UUID(tgt),
        ))

    return SubgraphResponse(
        root_id=root_id,
        root_identifier=root.node_identifier,
        max_depth=max_depth,
        node_count=len(sub_nodes),
        edge_count=len(sub_edges),
        nodes=sub_nodes,
        edges=sub_edges,
    )
