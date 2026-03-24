"""
conftest.py — shared pytest fixtures.

Key design decisions:
  - Uses an in-memory SQLite database so tests never touch graph.db
  - Each test function gets a clean database via the `db` fixture
  - The `client` fixture provides a FastAPI TestClient wired to the test db
  - The `seeded_db` fixture provides a pre-populated state for tests that
    need existing data to work with (e.g. compound endpoint tests)

How pytest fixtures work:
  - A fixture is a function decorated with @pytest.fixture
  - When a test function declares a fixture name as a parameter,
    pytest calls the fixture and passes its return value in automatically
  - `yield` fixtures run setup before the yield and teardown after
  - `scope="function"` (default) means a fresh fixture per test
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app


# ---------------------------------------------------------------------------
# Test database — in-memory SQLite, isolated per test
# ---------------------------------------------------------------------------

@pytest.fixture()
def db():
    """
    Provides a clean in-memory SQLite database for each test.
    All tables are created fresh, then dropped after the test completes.
    The StaticPool ensures the same connection is reused within a test,
    which is required for in-memory SQLite (each new connection sees an
    empty database).
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------------------------
# Test client — FastAPI TestClient wired to the test database
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(db):
    """
    Provides a FastAPI TestClient that uses the test database.

    The key trick here is overriding the `get_db` dependency — FastAPI's
    dependency injection system lets us swap out `get_db` at test time
    so that every request uses our isolated test database instead of graph.db.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass  # session lifecycle is managed by the `db` fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Seeded state — pre-populated database for compound endpoint tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def seeded(client):
    """
    Creates a minimal but complete graph in the test database:
      - 1 NodeType (HAZARD) with 2 property definitions assigned
      - 1 EdgeType (CAUSES)
      - 2 Nodes (HAZ-001, HAZ-002)
      - 1 Edge (CAUSES-001) connecting them
      - Property values set on HAZ-001

    Returns a dict of IDs so tests can reference created objects.
    Depends on `client` so it uses the same isolated test database.
    """
    # NodeType
    nt = client.post("/node-types/", json={
        "node_type_identifier": "HAZARD",
        "node_type_name": "Hazard",
        "node_type_description": "A hazard node",
        "created_by": "test",
    }).json()

    # EdgeType
    et = client.post("/edge-types/", json={
        "edge_type_identifier": "CAUSES",
        "edge_type_name": "Causes",
        "created_by": "test",
    }).json()

    # Property definitions
    p_id = client.post("/node-property-definitions/", json={
        "node_property_definition_identifier": "HAZ_ID",
        "node_property_definition_name": "Hazard ID",
        "node_property_definition_type": "string",
        "created_by": "test",
    }).json()

    p_severity = client.post("/node-property-definitions/", json={
        "node_property_definition_identifier": "SEVERITY",
        "node_property_definition_name": "Severity",
        "node_property_definition_type": "string",
        "node_property_definition_default_value": "Medium",
        "created_by": "test",
    }).json()

    # Assign properties to NodeType
    client.post("/node-type-property-assignments/", json={
        "node_type_id_fk": nt["id"],
        "node_property_definition_id_fk": p_id["id"],
        "is_required": True,
        "sort_order": 1,
        "created_by": "test",
    })
    client.post("/node-type-property-assignments/", json={
        "node_type_id_fk": nt["id"],
        "node_property_definition_id_fk": p_severity["id"],
        "is_required": False,
        "sort_order": 2,
        "default_value": "High",  # overrides definition default
        "created_by": "test",
    })

    # Nodes
    n1 = client.post("/nodes/", json={
        "node_type_id_fk": nt["id"],
        "node_identifier": "HAZ-001",
        "node_name": "Brake failure",
        "created_by": "test",
    }).json()

    n2 = client.post("/nodes/", json={
        "node_type_id_fk": nt["id"],
        "node_identifier": "HAZ-002",
        "node_name": "Signal failure",
        "created_by": "test",
    }).json()

    # Edge
    e1 = client.post("/edges/", json={
        "edge_type_id_fk": et["id"],
        "edge_identifier": "CAUSES-001",
        "edge_name": "Brake failure causes signal failure",
        "source_node_id_fk": n1["id"],
        "target_node_id_fk": n2["id"],
        "created_by": "test",
    }).json()

    # Property values on n1
    client.post("/node-property-values/", json={
        "node_id_fk": n1["id"],
        "node_property_definition_id_fk": p_id["id"],
        "node_property_value": "HAZ-001",
        "created_by": "test",
    })
    client.post("/node-property-values/", json={
        "node_id_fk": n1["id"],
        "node_property_definition_id_fk": p_severity["id"],
        "node_property_value": "Critical",
        "created_by": "test",
    })

    return {
        "node_type": nt,
        "edge_type": et,
        "prop_id": p_id,
        "prop_severity": p_severity,
        "node1": n1,
        "node2": n2,
        "edge1": e1,
    }