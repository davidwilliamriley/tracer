"""
test_node_type.py — CRUD tests for the NodeType endpoints.

This is the reference test file — the pattern used here
(arrange → act → assert, one behaviour per test) applies to
every other table. Once you understand this file the others
follow automatically.

Test naming convention:
    test_<endpoint>_<scenario>
    e.g. test_create_returns_201, test_create_duplicate_returns_409
"""


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def test_create_returns_201(client):
    r = client.post("/node-types/", json={
        "node_type_identifier": "SAFETY_REQ",
        "node_type_name": "Safety Requirement",
    })
    assert r.status_code == 201


def test_create_returns_correct_fields(client):
    r = client.post("/node-types/", json={
        "node_type_identifier": "SAFETY_REQ",
        "node_type_name": "Safety Requirement",
        "node_type_description": "A safety requirement",
        "created_by": "david",
    })
    body = r.json()
    assert body["node_type_identifier"] == "SAFETY_REQ"
    assert body["node_type_name"] == "Safety Requirement"
    assert body["node_type_description"] == "A safety requirement"
    assert body["created_by"] == "david"
    assert "id" in body
    assert "created_on" in body


def test_create_assigns_guid_id(client):
    r = client.post("/node-types/", json={
        "node_type_identifier": "SAFETY_REQ",
        "node_type_name": "Safety Requirement",
    })
    body = r.json()
    # UUID4 format: 8-4-4-4-12 hex chars
    assert len(body["id"]) == 36
    assert body["id"].count("-") == 4


def test_create_duplicate_identifier_returns_409(client):
    payload = {"node_type_identifier": "SAFETY_REQ", "node_type_name": "Safety Requirement"}
    client.post("/node-types/", json=payload)
    r = client.post("/node-types/", json=payload)
    assert r.status_code == 409


def test_create_duplicate_returns_conflict_error_shape(client):
    payload = {"node_type_identifier": "SAFETY_REQ", "node_type_name": "Safety Requirement"}
    client.post("/node-types/", json=payload)
    r = client.post("/node-types/", json=payload)
    body = r.json()
    assert body["error"] == "ConflictError"
    assert body["field"] == "node_type_identifier"
    assert "SAFETY_REQ" in body["message"]


def test_create_missing_required_fields_returns_422(client):
    r = client.post("/node-types/", json={})
    assert r.status_code == 422


def test_create_missing_fields_returns_validation_error_shape(client):
    r = client.post("/node-types/", json={})
    body = r.json()
    assert body["error"] == "ValidationError"
    assert "errors" in body
    field_names = [e["field"] for e in body["errors"]]
    assert "node_type_identifier" in field_names
    assert "node_type_name" in field_names


# ---------------------------------------------------------------------------
# READ — single
# ---------------------------------------------------------------------------

def test_get_returns_200(client):
    created = client.post("/node-types/", json={
        "node_type_identifier": "SAFETY_REQ",
        "node_type_name": "Safety Requirement",
    }).json()
    r = client.get(f"/node-types/{created['id']}")
    assert r.status_code == 200


def test_get_returns_correct_data(client):
    created = client.post("/node-types/", json={
        "node_type_identifier": "SAFETY_REQ",
        "node_type_name": "Safety Requirement",
    }).json()
    r = client.get(f"/node-types/{created['id']}")
    body = r.json()
    assert body["id"] == created["id"]
    assert body["node_type_identifier"] == "SAFETY_REQ"


def test_get_nonexistent_returns_404(client):
    r = client.get("/node-types/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_get_nonexistent_returns_not_found_error_shape(client):
    r = client.get("/node-types/00000000-0000-0000-0000-000000000000")
    body = r.json()
    assert body["error"] == "NotFoundError"
    assert body["status_code"] == 404


# ---------------------------------------------------------------------------
# READ — list with pagination
# ---------------------------------------------------------------------------

def test_list_returns_200(client):
    r = client.get("/node-types/")
    assert r.status_code == 200


def test_list_returns_pagination_shape(client):
    r = client.get("/node-types/")
    body = r.json()
    assert "items" in body
    assert "total" in body
    assert "skip" in body
    assert "limit" in body
    assert "has_more" in body


def test_list_empty_database(client):
    r = client.get("/node-types/")
    body = r.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["has_more"] is False


def test_list_returns_created_items(client):
    client.post("/node-types/", json={"node_type_identifier": "A", "node_type_name": "A"})
    client.post("/node-types/", json={"node_type_identifier": "B", "node_type_name": "B"})
    r = client.get("/node-types/")
    body = r.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_list_pagination_limit(client):
    for i in range(5):
        client.post("/node-types/", json={
            "node_type_identifier": f"TYPE_{i}",
            "node_type_name": f"Type {i}",
        })
    r = client.get("/node-types/?limit=2")
    body = r.json()
    assert len(body["items"]) == 2
    assert body["total"] == 5
    assert body["has_more"] is True


def test_list_pagination_skip(client):
    for i in range(3):
        client.post("/node-types/", json={
            "node_type_identifier": f"TYPE_{i}",
            "node_type_name": f"Type {i}",
        })
    r = client.get("/node-types/?skip=2&limit=10")
    body = r.json()
    assert len(body["items"]) == 1
    assert body["has_more"] is False


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def test_update_returns_200(client):
    created = client.post("/node-types/", json={
        "node_type_identifier": "SAFETY_REQ",
        "node_type_name": "Safety Requirement",
    }).json()
    r = client.put(f"/node-types/{created['id']}", json={
        "node_type_name": "Updated Name",
    })
    assert r.status_code == 200


def test_update_changes_correct_fields(client):
    created = client.post("/node-types/", json={
        "node_type_identifier": "SAFETY_REQ",
        "node_type_name": "Safety Requirement",
        "node_type_description": "Original description",
    }).json()
    r = client.put(f"/node-types/{created['id']}", json={
        "node_type_name": "Updated Name",
    })
    body = r.json()
    # Updated field changed
    assert body["node_type_name"] == "Updated Name"
    # Unchanged fields preserved
    assert body["node_type_description"] == "Original description"
    # Identifier never changes via update
    assert body["node_type_identifier"] == "SAFETY_REQ"


def test_update_nonexistent_returns_404(client):
    r = client.put(
        "/node-types/00000000-0000-0000-0000-000000000000",
        json={"node_type_name": "New Name"},
    )
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def test_delete_returns_200(client):
    created = client.post("/node-types/", json={
        "node_type_identifier": "SAFETY_REQ",
        "node_type_name": "Safety Requirement",
    }).json()
    r = client.delete(f"/node-types/{created['id']}")
    assert r.status_code == 200


def test_delete_removes_record(client):
    created = client.post("/node-types/", json={
        "node_type_identifier": "SAFETY_REQ",
        "node_type_name": "Safety Requirement",
    }).json()
    client.delete(f"/node-types/{created['id']}")
    r = client.get(f"/node-types/{created['id']}")
    assert r.status_code == 404


def test_delete_nonexistent_returns_404(client):
    r = client.delete("/node-types/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_delete_with_nodes_returns_400(client):
    """Cannot delete a NodeType that has nodes using it."""
    nt = client.post("/node-types/", json={
        "node_type_identifier": "SAFETY_REQ",
        "node_type_name": "Safety Requirement",
    }).json()
    client.post("/nodes/", json={
        "node_type_id_fk": nt["id"],
        "node_identifier": "SR-001",
        "node_name": "Test node",
    })
    r = client.delete(f"/node-types/{nt['id']}")
    assert r.status_code == 400


def test_delete_with_nodes_returns_dependency_error(client):
    nt = client.post("/node-types/", json={
        "node_type_identifier": "SAFETY_REQ",
        "node_type_name": "Safety Requirement",
    }).json()
    client.post("/nodes/", json={
        "node_type_id_fk": nt["id"],
        "node_identifier": "SR-001",
        "node_name": "Test node",
    })
    r = client.delete(f"/node-types/{nt['id']}")
    body = r.json()
    assert body["error"] == "DependencyError"