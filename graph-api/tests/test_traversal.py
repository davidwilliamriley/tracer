"""
test_traversal.py

Tests for the graph traversal endpoints:
  GET /nodes/{id}/neighbours
  GET /nodes/{id}/paths?target={id}
  GET /nodes/{id}/subgraph?max_depth={n}

Uses a custom `graph` fixture that builds a richer topology than
the `seeded` fixture — we need multiple hops to properly test
path finding and subgraph depth limiting.

Graph topology used in these tests:

    A --CAUSES--> B --CAUSES--> C --CAUSES--> D
                  |
                  +--CAUSES--> E

  - A → B → C → D  (chain of 3 hops)
  - B → E           (branch)
  - A is source, D and E are sinks
  - No path from D back to A (directed)
"""
import pytest


@pytest.fixture()
def graph(client):
    """
    Build a test graph with enough topology to exercise all traversal cases.
    Returns a dict of created object IDs.
    """
    nt = client.post("/node-types/", json={
        "node_type_identifier": "COMPONENT",
        "node_type_name": "Component",
    }).json()
    et = client.post("/edge-types/", json={
        "edge_type_identifier": "DEPENDS_ON",
        "edge_type_name": "Depends On",
    }).json()

    def make_node(identifier, name):
        return client.post("/nodes/", json={
            "node_type_id_fk": nt["id"],
            "node_identifier": identifier,
            "node_name": name,
        }).json()

    def make_edge(identifier, source_id, target_id):
        return client.post("/edges/", json={
            "edge_type_id_fk": et["id"],
            "edge_identifier": identifier,
            "edge_name": identifier,
            "source_node_id_fk": source_id,
            "target_node_id_fk": target_id,
        }).json()

    a = make_node("A", "Node A")
    b = make_node("B", "Node B")
    c = make_node("C", "Node C")
    d = make_node("D", "Node D")
    e = make_node("E", "Node E")

    ab = make_edge("A-B", a["id"], b["id"])
    bc = make_edge("B-C", b["id"], c["id"])
    cd = make_edge("C-D", c["id"], d["id"])
    be = make_edge("B-E", b["id"], e["id"])

    return {
        "node_type": nt, "edge_type": et,
        "a": a, "b": b, "c": c, "d": d, "e": e,
        "ab": ab, "bc": bc, "cd": cd, "be": be,
    }


# ---------------------------------------------------------------------------
# Neighbours
# ---------------------------------------------------------------------------

class TestNeighbours:

    def test_returns_200(self, client, graph):
        r = client.get(f'/nodes/{graph["b"]["id"]}/neighbours')
        assert r.status_code == 200

    def test_response_shape(self, client, graph):
        r = client.get(f'/nodes/{graph["b"]["id"]}/neighbours')
        body = r.json()
        assert "node_id" in body
        assert "node_identifier" in body
        assert "neighbour_count" in body
        assert "neighbours" in body

    def test_node_b_has_three_neighbours(self, client, graph):
        """B connects to: A (incoming), C (outgoing), E (outgoing)."""
        r = client.get(f'/nodes/{graph["b"]["id"]}/neighbours')
        body = r.json()
        assert body["neighbour_count"] == 3

    def test_node_a_has_one_neighbour(self, client, graph):
        """A only connects to B (outgoing). Nothing points to A."""
        r = client.get(f'/nodes/{graph["a"]["id"]}/neighbours')
        body = r.json()
        assert body["neighbour_count"] == 1

    def test_sink_node_has_one_neighbour(self, client, graph):
        """D is a sink — only C points to it (incoming)."""
        r = client.get(f'/nodes/{graph["d"]["id"]}/neighbours')
        body = r.json()
        assert body["neighbour_count"] == 1

    def test_direction_labels_correct(self, client, graph):
        """B → C should appear as outgoing from B's perspective."""
        r = client.get(f'/nodes/{graph["b"]["id"]}/neighbours')
        neighbours = r.json()["neighbours"]
        # Find C in the neighbour list
        c_entry = next(
            (n for n in neighbours if n["identifier"] == "C"), None
        )
        assert c_entry is not None
        directions = [e["direction"] for e in c_entry["edges"]]
        assert "outgoing" in directions

    def test_incoming_direction_label(self, client, graph):
        """A → B: from B's perspective, A is an incoming neighbour."""
        r = client.get(f'/nodes/{graph["b"]["id"]}/neighbours')
        neighbours = r.json()["neighbours"]
        a_entry = next(
            (n for n in neighbours if n["identifier"] == "A"), None
        )
        assert a_entry is not None
        directions = [e["direction"] for e in a_entry["edges"]]
        assert "incoming" in directions

    def test_isolated_node_has_no_neighbours(self, client, graph):
        """A node with no edges should return neighbour_count=0."""
        nt_id = graph["node_type"]["id"]
        isolated = client.post("/nodes/", json={
            "node_type_id_fk": nt_id,
            "node_identifier": "ISOLATED",
            "node_name": "Isolated Node",
        }).json()
        r = client.get(f'/nodes/{isolated["id"]}/neighbours')
        body = r.json()
        assert body["neighbour_count"] == 0
        assert body["neighbours"] == []

    def test_nonexistent_node_returns_404(self, client, graph):
        r = client.get("/nodes/00000000-0000-0000-0000-000000000000/neighbours")
        assert r.status_code == 404

    def test_neighbour_contains_type_info(self, client, graph):
        r = client.get(f'/nodes/{graph["a"]["id"]}/neighbours')
        neighbour = r.json()["neighbours"][0]
        assert "type_identifier" in neighbour
        assert "type_name" in neighbour
        assert neighbour["type_identifier"] == "COMPONENT"


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

class TestPaths:

    def test_returns_200(self, client, graph):
        r = client.get(
            f'/nodes/{graph["a"]["id"]}/paths?target={graph["d"]["id"]}'
        )
        assert r.status_code == 200

    def test_response_shape(self, client, graph):
        r = client.get(
            f'/nodes/{graph["a"]["id"]}/paths?target={graph["d"]["id"]}'
        )
        body = r.json()
        assert "source_id" in body
        assert "target_id" in body
        assert "found" in body
        assert "hop_count" in body
        assert "nodes" in body
        assert "edges" in body

    def test_direct_path_found(self, client, graph):
        """A → B is a single hop."""
        r = client.get(
            f'/nodes/{graph["a"]["id"]}/paths?target={graph["b"]["id"]}'
        )
        body = r.json()
        assert body["found"] is True
        assert body["hop_count"] == 1

    def test_multi_hop_path_found(self, client, graph):
        """A → B → C → D is 3 hops."""
        r = client.get(
            f'/nodes/{graph["a"]["id"]}/paths?target={graph["d"]["id"]}'
        )
        body = r.json()
        assert body["found"] is True
        assert body["hop_count"] == 3

    def test_path_nodes_in_order(self, client, graph):
        """Path from A to D should list nodes A, B, C, D in order."""
        r = client.get(
            f'/nodes/{graph["a"]["id"]}/paths?target={graph["d"]["id"]}'
        )
        identifiers = [n["identifier"] for n in r.json()["nodes"]]
        assert identifiers == ["A", "B", "C", "D"]

    def test_path_edges_in_order(self, client, graph):
        """Path A → B → C → D should include edges A-B, B-C, C-D."""
        r = client.get(
            f'/nodes/{graph["a"]["id"]}/paths?target={graph["d"]["id"]}'
        )
        edge_identifiers = [e["identifier"] for e in r.json()["edges"]]
        assert edge_identifiers == ["A-B", "B-C", "C-D"]

    def test_no_reverse_path(self, client, graph):
        """D → A has no directed path — edges only go A→B→C→D."""
        r = client.get(
            f'/nodes/{graph["d"]["id"]}/paths?target={graph["a"]["id"]}'
        )
        body = r.json()
        assert body["found"] is False
        assert body["hop_count"] == 0
        assert body["nodes"] == []
        assert body["edges"] == []

    def test_same_source_and_target_returns_400(self, client, graph):
        node_id = graph["a"]["id"]
        r = client.get(f'/nodes/{node_id}/paths?target={node_id}')
        assert r.status_code == 422

    def test_missing_target_param_returns_422(self, client, graph):
        r = client.get(f'/nodes/{graph["a"]["id"]}/paths')
        assert r.status_code == 422

    def test_nonexistent_source_returns_404(self, client, graph):
        r = client.get(
            f'/nodes/00000000-0000-0000-0000-000000000000/paths'
            f'?target={graph["b"]["id"]}'
        )
        assert r.status_code == 404

    def test_nonexistent_target_returns_404(self, client, graph):
        r = client.get(
            f'/nodes/{graph["a"]["id"]}/paths'
            f'?target=00000000-0000-0000-0000-000000000000'
        )
        assert r.status_code == 404


# ---------------------------------------------------------------------------
# Subgraph
# ---------------------------------------------------------------------------

class TestSubgraph:

    def test_returns_200(self, client, graph):
        r = client.get(f'/nodes/{graph["a"]["id"]}/subgraph')
        assert r.status_code == 200

    def test_response_shape(self, client, graph):
        r = client.get(f'/nodes/{graph["a"]["id"]}/subgraph')
        body = r.json()
        assert "root_id" in body
        assert "root_identifier" in body
        assert "max_depth" in body
        assert "node_count" in body
        assert "edge_count" in body
        assert "nodes" in body
        assert "edges" in body

    def test_full_reachability_from_a(self, client, graph):
        """From A with max_depth=5: A, B, C, D, E all reachable."""
        r = client.get(f'/nodes/{graph["a"]["id"]}/subgraph?max_depth=5')
        body = r.json()
        assert body["node_count"] == 5
        identifiers = {n["identifier"] for n in body["nodes"]}
        assert identifiers == {"A", "B", "C", "D", "E"}

    def test_depth_1_from_a(self, client, graph):
        """From A with max_depth=1: only A and B (one hop)."""
        r = client.get(f'/nodes/{graph["a"]["id"]}/subgraph?max_depth=1')
        body = r.json()
        identifiers = {n["identifier"] for n in body["nodes"]}
        assert identifiers == {"A", "B"}

    def test_depth_2_from_a(self, client, graph):
        """From A with max_depth=2: A, B, C, E (two hops)."""
        r = client.get(f'/nodes/{graph["a"]["id"]}/subgraph?max_depth=2')
        body = r.json()
        identifiers = {n["identifier"] for n in body["nodes"]}
        assert identifiers == {"A", "B", "C", "E"}

    def test_from_sink_node_returns_only_itself(self, client, graph):
        """D has no outgoing edges — subgraph is just D."""
        r = client.get(f'/nodes/{graph["d"]["id"]}/subgraph?max_depth=5')
        body = r.json()
        assert body["node_count"] == 1
        assert body["nodes"][0]["identifier"] == "D"

    def test_root_always_included(self, client, graph):
        """The root node itself is always included regardless of depth."""
        r = client.get(f'/nodes/{graph["a"]["id"]}/subgraph?max_depth=1')
        identifiers = {n["identifier"] for n in r.json()["nodes"]}
        assert "A" in identifiers

    def test_max_depth_exceeding_20_returns_422(self, client, graph):
        r = client.get(f'/nodes/{graph["a"]["id"]}/subgraph?max_depth=21')
        assert r.status_code == 422

    def test_max_depth_0_returns_422(self, client, graph):
        r = client.get(f'/nodes/{graph["a"]["id"]}/subgraph?max_depth=0')
        assert r.status_code == 422

    def test_nonexistent_node_returns_404(self, client, graph):
        r = client.get(
            "/nodes/00000000-0000-0000-0000-000000000000/subgraph"
        )
        assert r.status_code == 404

    def test_edge_count_correct(self, client, graph):
        """From A with depth 5: all 4 edges included."""
        r = client.get(f'/nodes/{graph["a"]["id"]}/subgraph?max_depth=5')
        assert r.json()["edge_count"] == 4
