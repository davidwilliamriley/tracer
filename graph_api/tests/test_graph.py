"""
test_graph.py — tests for the compound endpoints in routers/graph.py.

These test the most important Phase 1 endpoints:
  - GET /nodes/{id}/full
  - GET /edges/{id}/full
  - GET /node-types/{id}/form-schema
  - GET /edge-types/{id}/form-schema
  - POST /nodes/{id}/properties  (bulk write)
  - POST /edges/{id}/properties
  - GET /graph

All tests use the `seeded` fixture from conftest.py which provides
a pre-populated database with a NodeType, EdgeType, 2 nodes, 1 edge,
and property values already set on node1.
"""


# ---------------------------------------------------------------------------
# Node full
# ---------------------------------------------------------------------------

def test_node_full_returns_200(client, seeded):
    node_id = seeded["node1"]["id"]
    r = client.get(f"/nodes/{node_id}/full")
    assert r.status_code == 200


def test_node_full_contains_type_metadata(client, seeded):
    node_id = seeded["node1"]["id"]
    r = client.get(f"/nodes/{node_id}/full")
    body = r.json()
    assert body["node_type_identifier"] == "HAZARD"
    assert body["node_type_name"] == "Hazard"


def test_node_full_contains_properties(client, seeded):
    node_id = seeded["node1"]["id"]
    r = client.get(f"/nodes/{node_id}/full")
    body = r.json()
    assert len(body["properties"]) == 2


def test_node_full_properties_have_correct_values(client, seeded):
    node_id = seeded["node1"]["id"]
    r = client.get(f"/nodes/{node_id}/full")
    props = {p["identifier"]: p["value"] for p in r.json()["properties"]}
    assert props["HAZ_ID"] == "HAZ-001"
    assert props["SEVERITY"] == "Critical"


def test_node_full_properties_ordered_by_sort_order(client, seeded):
    node_id = seeded["node1"]["id"]
    r = client.get(f"/nodes/{node_id}/full")
    sort_orders = [p["sort_order"] for p in r.json()["properties"]]
    assert sort_orders == sorted(sort_orders)


def test_node_full_includes_required_flag(client, seeded):
    node_id = seeded["node1"]["id"]
    r = client.get(f"/nodes/{node_id}/full")
    props = {p["identifier"]: p for p in r.json()["properties"]}
    assert props["HAZ_ID"]["is_required"] is True
    assert props["SEVERITY"]["is_required"] is False


def test_node_full_node_without_values_returns_null_values(client, seeded):
    """Node2 has no property values set — values should be null."""
    node_id = seeded["node2"]["id"]
    r = client.get(f"/nodes/{node_id}/full")
    body = r.json()
    assert body["node_identifier"] == "HAZ-002"
    # Properties should still appear (from assignments) but with null values
    assert len(body["properties"]) == 2
    for p in body["properties"]:
        assert p["value"] is None


def test_node_full_nonexistent_returns_404(client, seeded):
    r = client.get("/nodes/00000000-0000-0000-0000-000000000000/full")
    assert r.status_code == 404
    assert r.json()["error"] == "NotFoundError"


# ---------------------------------------------------------------------------
# Edge full
# ---------------------------------------------------------------------------

def test_edge_full_returns_200(client, seeded):
    edge_id = seeded["edge1"]["id"]
    r = client.get(f"/edges/{edge_id}/full")
    assert r.status_code == 200


def test_edge_full_contains_source_and_target_names(client, seeded):
    edge_id = seeded["edge1"]["id"]
    r = client.get(f"/edges/{edge_id}/full")
    body = r.json()
    assert body["source_node_name"] == "Brake failure"
    assert body["target_node_name"] == "Signal failure"
    assert body["source_node_identifier"] == "HAZ-001"
    assert body["target_node_identifier"] == "HAZ-002"


def test_edge_full_contains_type_metadata(client, seeded):
    edge_id = seeded["edge1"]["id"]
    r = client.get(f"/edges/{edge_id}/full")
    body = r.json()
    assert body["edge_type_identifier"] == "CAUSES"
    assert body["edge_type_name"] == "Causes"


def test_edge_full_nonexistent_returns_404(client, seeded):
    r = client.get("/edges/00000000-0000-0000-0000-000000000000/full")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Form schema
# ---------------------------------------------------------------------------

def test_form_schema_returns_200(client, seeded):
    nt_id = seeded["node_type"]["id"]
    r = client.get(f"/node-types/{nt_id}/form-schema")
    assert r.status_code == 200


def test_form_schema_contains_type_info(client, seeded):
    nt_id = seeded["node_type"]["id"]
    r = client.get(f"/node-types/{nt_id}/form-schema")
    body = r.json()
    assert body["type_identifier"] == "HAZARD"
    assert body["type_name"] == "Hazard"


def test_form_schema_returns_correct_field_count(client, seeded):
    nt_id = seeded["node_type"]["id"]
    r = client.get(f"/node-types/{nt_id}/form-schema")
    assert len(r.json()["fields"]) == 2


def test_form_schema_fields_ordered_by_sort_order(client, seeded):
    nt_id = seeded["node_type"]["id"]
    r = client.get(f"/node-types/{nt_id}/form-schema")
    orders = [f["sort_order"] for f in r.json()["fields"]]
    assert orders == sorted(orders)


def test_form_schema_assignment_default_overrides_definition_default(client, seeded):
    """
    The SEVERITY property has definition default='Medium' but
    the assignment sets default='High'. The form schema should
    return 'High' — the assignment value takes precedence.
    """
    nt_id = seeded["node_type"]["id"]
    r = client.get(f"/node-types/{nt_id}/form-schema")
    fields = {f["identifier"]: f for f in r.json()["fields"]}
    assert fields["SEVERITY"]["default_value"] == "High"


def test_form_schema_required_flag_correct(client, seeded):
    nt_id = seeded["node_type"]["id"]
    r = client.get(f"/node-types/{nt_id}/form-schema")
    fields = {f["identifier"]: f for f in r.json()["fields"]}
    assert fields["HAZ_ID"]["is_required"] is True
    assert fields["SEVERITY"]["is_required"] is False


def test_form_schema_empty_type_returns_no_fields(client):
    """A NodeType with no assignments should return an empty fields list."""
    nt = client.post("/node-types/", json={
        "node_type_identifier": "EMPTY_TYPE",
        "node_type_name": "Empty Type",
    }).json()
    r = client.get(f"/node-types/{nt['id']}/form-schema")
    assert r.status_code == 200
    assert r.json()["fields"] == []


def test_form_schema_nonexistent_type_returns_404(client):
    r = client.get("/node-types/00000000-0000-0000-0000-000000000000/form-schema")
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Bulk property write
# ---------------------------------------------------------------------------

def test_bulk_write_returns_200(client, seeded):
    node_id = seeded["node2"]["id"]
    prop_id = seeded["prop_id"]["id"]
    r = client.post(f"/nodes/{node_id}/properties", json={
        "properties": [{"definition_id": prop_id, "value": "HAZ-002"}],
        "modified_by": "test",
    })
    assert r.status_code == 200


def test_bulk_write_returns_node_full(client, seeded):
    """Bulk write should return the full node so the frontend can update state."""
    node_id = seeded["node2"]["id"]
    prop_id = seeded["prop_id"]["id"]
    r = client.post(f"/nodes/{node_id}/properties", json={
        "properties": [{"definition_id": prop_id, "value": "HAZ-002"}],
    })
    body = r.json()
    assert "properties" in body
    assert "node_type_identifier" in body


def test_bulk_write_values_persisted(client, seeded):
    node_id = seeded["node2"]["id"]
    prop_id = seeded["prop_id"]["id"]
    prop_sev = seeded["prop_severity"]["id"]

    client.post(f"/nodes/{node_id}/properties", json={
        "properties": [
            {"definition_id": prop_id, "value": "HAZ-002"},
            {"definition_id": prop_sev, "value": "Low"},
        ],
    })

    # Verify with a follow-up GET /full
    r = client.get(f"/nodes/{node_id}/full")
    props = {p["identifier"]: p["value"] for p in r.json()["properties"]}
    assert props["HAZ_ID"] == "HAZ-002"
    assert props["SEVERITY"] == "Low"


def test_bulk_write_is_idempotent(client, seeded):
    """Calling bulk write twice with the same values should not error."""
    node_id = seeded["node1"]["id"]
    prop_id = seeded["prop_id"]["id"]
    payload = {"properties": [{"definition_id": prop_id, "value": "HAZ-001"}]}

    r1 = client.post(f"/nodes/{node_id}/properties", json=payload)
    r2 = client.post(f"/nodes/{node_id}/properties", json=payload)
    assert r1.status_code == 200
    assert r2.status_code == 200


def test_bulk_write_updates_existing_values(client, seeded):
    """Writing to a node that already has values should update them."""
    node_id = seeded["node1"]["id"]
    prop_id = seeded["prop_id"]["id"]
    prop_sev = seeded["prop_severity"]["id"]

    # Must include HAZ_ID (required) alongside SEVERITY
    client.post(f"/nodes/{node_id}/properties", json={
        "properties": [
            {"definition_id": prop_id, "value": "HAZ-001"},
            {"definition_id": prop_sev, "value": "Low"},
        ],
    })

    r = client.get(f"/nodes/{node_id}/full")
    props = {p["identifier"]: p["value"] for p in r.json()["properties"]}
    assert props["SEVERITY"] == "Low"


def test_bulk_write_invalid_node_returns_404(client, seeded):
    prop_id = seeded["prop_id"]["id"]
    r = client.post("/nodes/00000000-0000-0000-0000-000000000000/properties", json={
        "properties": [{"definition_id": prop_id, "value": "X"}],
    })
    assert r.status_code == 404


def test_bulk_write_invalid_definition_returns_404(client, seeded):
    node_id = seeded["node1"]["id"]
    r = client.post(f"/nodes/{node_id}/properties", json={
        "properties": [{"definition_id": "00000000-0000-0000-0000-000000000000", "value": "X"}],
    })
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Graph topology
# ---------------------------------------------------------------------------

def test_graph_returns_200(client, seeded):
    r = client.get("/graph")
    assert r.status_code == 200


def test_graph_returns_correct_shape(client, seeded):
    r = client.get("/graph")
    body = r.json()
    assert "nodes" in body
    assert "edges" in body
    assert "node_count" in body
    assert "edge_count" in body


def test_graph_node_count_matches(client, seeded):
    r = client.get("/graph")
    body = r.json()
    assert body["node_count"] == 2
    assert len(body["nodes"]) == 2


def test_graph_edge_count_matches(client, seeded):
    r = client.get("/graph")
    body = r.json()
    assert body["edge_count"] == 1
    assert len(body["edges"]) == 1


def test_graph_nodes_contain_type_info(client, seeded):
    r = client.get("/graph")
    node = r.json()["nodes"][0]
    assert "type_identifier" in node
    assert "type_name" in node
    assert node["type_identifier"] == "HAZARD"


def test_graph_edges_have_source_and_target(client, seeded):
    r = client.get("/graph")
    edge = r.json()["edges"][0]
    assert "source" in edge
    assert "target" in edge
    assert edge["source"] == seeded["node1"]["id"]
    assert edge["target"] == seeded["node2"]["id"]


def test_graph_empty_database(client):
    """Graph with no data should return empty lists, not an error."""
    r = client.get("/graph")
    body = r.json()
    assert r.status_code == 200
    assert body["node_count"] == 0
    assert body["edge_count"] == 0
    assert body["nodes"] == []
    assert body["edges"] == []
