"""
test_search.py

Tests for search and filter query parameters on the node and edge list endpoints:
  GET /nodes/?node_type_identifier=X
  GET /nodes/?name_contains=X
  GET /nodes/?identifier_contains=X
  GET /edges/?edge_type_identifier=X
  GET /edges/?name_contains=X
  GET /edges/?source_node_id=X
  GET /edges/?target_node_id=X

Filters can be combined — multiple filters AND together.
"""
import pytest


@pytest.fixture()
def populated(client):
    """
    Create a dataset with enough variety to test filtering.

    NodeTypes: HAZARD, REQUIREMENT
    EdgeTypes:  CAUSES, MITIGATES
    Nodes:
      - HAZ-001 (HAZARD): "Brake failure"
      - HAZ-002 (HAZARD): "Signal failure"
      - REQ-001 (REQUIREMENT): "Braking distance"
      - REQ-002 (REQUIREMENT): "Emergency stop"
    Edges:
      - HAZ-001 --CAUSES--> HAZ-002
      - REQ-001 --MITIGATES--> HAZ-001
      - REQ-002 --MITIGATES--> HAZ-002
    """
    nt_haz = client.post("/node-types/", json={
        "node_type_identifier": "HAZARD",
        "node_type_name": "Hazard",
    }).json()
    nt_req = client.post("/node-types/", json={
        "node_type_identifier": "REQUIREMENT",
        "node_type_name": "Requirement",
    }).json()
    et_causes = client.post("/edge-types/", json={
        "edge_type_identifier": "CAUSES",
        "edge_type_name": "Causes",
    }).json()
    et_mitigates = client.post("/edge-types/", json={
        "edge_type_identifier": "MITIGATES",
        "edge_type_name": "Mitigates",
    }).json()

    def node(identifier, name, nt_id):
        return client.post("/nodes/", json={
            "node_type_id_fk": nt_id,
            "node_identifier": identifier,
            "node_name": name,
        }).json()

    def edge(identifier, name, et_id, src, tgt):
        return client.post("/edges/", json={
            "edge_type_id_fk": et_id,
            "edge_identifier": identifier,
            "edge_name": name,
            "source_node_id_fk": src,
            "target_node_id_fk": tgt,
        }).json()

    h1 = node("HAZ-001", "Brake failure", nt_haz["id"])
    h2 = node("HAZ-002", "Signal failure", nt_haz["id"])
    r1 = node("REQ-001", "Braking distance", nt_req["id"])
    r2 = node("REQ-002", "Emergency stop", nt_req["id"])

    e1 = edge("CAUSES-001", "Brake causes signal", et_causes["id"], h1["id"], h2["id"])
    e2 = edge("MIT-001", "Braking distance mitigates brake failure", et_mitigates["id"], r1["id"], h1["id"])
    e3 = edge("MIT-002", "Emergency stop mitigates signal failure", et_mitigates["id"], r2["id"], h2["id"])

    return {
        "nt_haz": nt_haz, "nt_req": nt_req,
        "et_causes": et_causes, "et_mitigates": et_mitigates,
        "h1": h1, "h2": h2, "r1": r1, "r2": r2,
        "e1": e1, "e2": e2, "e3": e3,
    }


# ---------------------------------------------------------------------------
# Node filtering
# ---------------------------------------------------------------------------

class TestNodeFilter:

    def test_no_filter_returns_all(self, client, populated):
        r = client.get("/nodes/")
        assert r.json()["total"] == 4

    def test_filter_by_node_type_identifier(self, client, populated):
        r = client.get("/nodes/?node_type_identifier=HAZARD")
        body = r.json()
        assert body["total"] == 2
        identifiers = {n["node_identifier"] for n in body["items"]}
        assert identifiers == {"HAZ-001", "HAZ-002"}

    def test_filter_by_requirement_type(self, client, populated):
        r = client.get("/nodes/?node_type_identifier=REQUIREMENT")
        body = r.json()
        assert body["total"] == 2
        identifiers = {n["node_identifier"] for n in body["items"]}
        assert identifiers == {"REQ-001", "REQ-002"}

    def test_filter_by_nonexistent_type_returns_empty(self, client, populated):
        r = client.get("/nodes/?node_type_identifier=DOESNOTEXIST")
        body = r.json()
        assert body["total"] == 0
        assert body["items"] == []

    def test_filter_by_name_contains(self, client, populated):
        r = client.get("/nodes/?name_contains=failure")
        body = r.json()
        assert body["total"] == 2
        names = {n["node_name"] for n in body["items"]}
        assert "Brake failure" in names
        assert "Signal failure" in names

    def test_name_contains_case_insensitive(self, client, populated):
        r = client.get("/nodes/?name_contains=FAILURE")
        assert r.json()["total"] == 2

    def test_filter_by_identifier_contains(self, client, populated):
        r = client.get("/nodes/?identifier_contains=HAZ")
        body = r.json()
        assert body["total"] == 2

    def test_combined_type_and_name_filter(self, client, populated):
        """HAZARD type AND name contains 'brake' — should return only HAZ-001."""
        r = client.get("/nodes/?node_type_identifier=HAZARD&name_contains=brake")
        body = r.json()
        assert body["total"] == 1
        assert body["items"][0]["node_identifier"] == "HAZ-001"

    def test_filter_respects_pagination(self, client, populated):
        r = client.get("/nodes/?node_type_identifier=HAZARD&limit=1")
        body = r.json()
        assert len(body["items"]) == 1
        assert body["total"] == 2
        assert body["has_more"] is True

    def test_filter_returns_pagination_shape(self, client, populated):
        r = client.get("/nodes/?node_type_identifier=HAZARD")
        body = r.json()
        assert "items" in body
        assert "total" in body
        assert "has_more" in body


# ---------------------------------------------------------------------------
# Edge filtering
# ---------------------------------------------------------------------------

class TestEdgeFilter:

    def test_no_filter_returns_all(self, client, populated):
        r = client.get("/edges/")
        assert r.json()["total"] == 3

    def test_filter_by_edge_type_identifier(self, client, populated):
        r = client.get("/edges/?edge_type_identifier=MITIGATES")
        body = r.json()
        assert body["total"] == 2
        identifiers = {e["edge_identifier"] for e in body["items"]}
        assert identifiers == {"MIT-001", "MIT-002"}

    def test_filter_by_causes_type(self, client, populated):
        r = client.get("/edges/?edge_type_identifier=CAUSES")
        body = r.json()
        assert body["total"] == 1
        assert body["items"][0]["edge_identifier"] == "CAUSES-001"

    def test_filter_by_nonexistent_type_returns_empty(self, client, populated):
        r = client.get("/edges/?edge_type_identifier=DOESNOTEXIST")
        assert r.json()["total"] == 0

    def test_filter_by_name_contains(self, client, populated):
        r = client.get("/edges/?name_contains=brake")
        body = r.json()
        # "Brake causes signal" and "Braking distance mitigates brake failure"
        assert body["total"] == 2

    def test_name_filter_case_insensitive(self, client, populated):
        r = client.get("/edges/?name_contains=BRAKE")
        assert r.json()["total"] == 2

    def test_filter_by_source_node_id(self, client, populated):
        source_id = populated["h1"]["id"]
        r = client.get(f"/edges/?source_node_id={source_id}")
        body = r.json()
        assert body["total"] == 1
        assert body["items"][0]["edge_identifier"] == "CAUSES-001"

    def test_filter_by_target_node_id(self, client, populated):
        target_id = populated["h2"]["id"]
        r = client.get(f"/edges/?target_node_id={target_id}")
        body = r.json()
        assert body["total"] == 2
        identifiers = {e["edge_identifier"] for e in body["items"]}
        assert identifiers == {"CAUSES-001", "MIT-002"}

    def test_combined_type_and_target_filter(self, client, populated):
        """MITIGATES edges targeting h1 — should be MIT-001 only."""
        r = client.get(
            f'/edges/?edge_type_identifier=MITIGATES'
            f'&target_node_id={populated["h1"]["id"]}'
        )
        body = r.json()
        assert body["total"] == 1
        assert body["items"][0]["edge_identifier"] == "MIT-001"

    def test_filter_respects_pagination(self, client, populated):
        r = client.get("/edges/?edge_type_identifier=MITIGATES&limit=1")
        body = r.json()
        assert len(body["items"]) == 1
        assert body["total"] == 2
        assert body["has_more"] is True
