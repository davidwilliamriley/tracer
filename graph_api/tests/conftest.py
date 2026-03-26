"""
conftest.py — shared pytest fixtures.

Auth changes in Phase 3:
  - The `client` fixture now logs in after creating the TestClient and
    sets the Authorization header on all subsequent requests.
  - The test credentials match the defaults in config.py / .env so no
    extra setup is needed to run the suite locally.
  - The `auth_headers` fixture is exposed separately so individual tests
    can use it if they need to make raw requests without the header.
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
# Test client — authenticated, wired to the test database
# ---------------------------------------------------------------------------

@pytest.fixture()
def client(db):
    """
    Provides an authenticated FastAPI TestClient.

    Two things happen here:
      1. The get_db dependency is overridden to use the in-memory test DB.
      2. After the client is created, we log in with the dev credentials
         and set the Authorization header so all subsequent requests
         automatically include the token.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app, raise_server_exceptions=False) as test_client:
        # Log in and attach the token to all future requests
        response = test_client.post(
            "/auth/token",
            data={"username": "admin", "password": "tracer-dev-password"},
        )
        assert response.status_code == 200, (
            f"Test login failed: {response.status_code} {response.text}"
        )
        token = response.json()["access_token"]
        test_client.headers["Authorization"] = f"Bearer {token}"
        yield test_client

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Auth headers fixture — for tests that need explicit header control
# ---------------------------------------------------------------------------

@pytest.fixture()
def auth_headers(client):
    """
    Returns the Authorization header dict for use in raw requests.
    Usually you won't need this — `client` already has the header set.
    Useful when testing auth failure scenarios where you want to
    make a request WITHOUT the header.
    """
    return {"Authorization": client.headers["Authorization"]}


# ---------------------------------------------------------------------------
# Seeded state — pre-populated database for compound endpoint tests
# ---------------------------------------------------------------------------

@pytest.fixture()
def seeded(client):
    """
    Creates a minimal but complete graph in the test database.
    Returns a dict of IDs so tests can reference created objects.
    """
    nt = client.post("/node-types/", json={
        "node_type_identifier": "HAZARD",
        "node_type_name": "Hazard",
        "node_type_description": "A hazard node",
        "created_by": "test",
    }).json()

    et = client.post("/edge-types/", json={
        "edge_type_identifier": "CAUSES",
        "edge_type_name": "Causes",
        "created_by": "test",
    }).json()

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
        "default_value": "High",
        "created_by": "test",
    })

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

    e1 = client.post("/edges/", json={
        "edge_type_id_fk": et["id"],
        "edge_identifier": "CAUSES-001",
        "edge_name": "Brake failure causes signal failure",
        "source_node_id_fk": n1["id"],
        "target_node_id_fk": n2["id"],
        "created_by": "test",
    }).json()

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
