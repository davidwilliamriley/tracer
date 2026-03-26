"""
test_auth.py — tests for authentication endpoints and protection.

Covers:
  POST /auth/token   — login
  POST /auth/refresh — token refresh
  GET  /auth/me      — current user
  Protected route behaviour — 401 without token, 200 with valid token
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app


# ---------------------------------------------------------------------------
# Unauthenticated client fixture — for testing 401 responses
# ---------------------------------------------------------------------------

@pytest.fixture()
def raw_client(db):
    """A TestClient with NO Authorization header set."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

class TestLogin:

    def test_valid_credentials_return_200(self, raw_client):
        r = raw_client.post(
            "/auth/token",
            data={"username": "admin", "password": "tracer-dev-password"},
        )
        assert r.status_code == 200

    def test_login_returns_token_shape(self, raw_client):
        r = raw_client.post(
            "/auth/token",
            data={"username": "admin", "password": "tracer-dev-password"},
        )
        body = r.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"
        assert "expires_in" in body

    def test_access_token_is_non_empty_string(self, raw_client):
        r = raw_client.post(
            "/auth/token",
            data={"username": "admin", "password": "tracer-dev-password"},
        )
        token = r.json()["access_token"]
        assert isinstance(token, str)
        assert len(token) > 20

    def test_wrong_password_returns_401(self, raw_client):
        r = raw_client.post(
            "/auth/token",
            data={"username": "admin", "password": "wrong-password"},
        )
        assert r.status_code == 401

    def test_wrong_username_returns_401(self, raw_client):
        r = raw_client.post(
            "/auth/token",
            data={"username": "notauser", "password": "tracer-dev-password"},
        )
        assert r.status_code == 401

    def test_wrong_credentials_return_auth_error(self, raw_client):
        r = raw_client.post(
            "/auth/token",
            data={"username": "admin", "password": "wrong"},
        )
        body = r.json()
        assert body["error"] == "AuthError"

    def test_missing_credentials_return_422(self, raw_client):
        r = raw_client.post("/auth/token", data={})
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# Token refresh
# ---------------------------------------------------------------------------

class TestRefresh:

    def test_valid_refresh_token_returns_200(self, raw_client):
        login = raw_client.post(
            "/auth/token",
            data={"username": "admin", "password": "tracer-dev-password"},
        ).json()
        r = raw_client.post(
            "/auth/refresh",
            json={"refresh_token": login["refresh_token"]},
        )
        assert r.status_code == 200

    def test_refresh_returns_new_access_token(self, raw_client):
        """Refreshing should return a valid access token."""
        login = raw_client.post(
            "/auth/token",
            data={"username": "admin", "password": "tracer-dev-password"},
        ).json()
        r = raw_client.post(
            "/auth/refresh",
            json={"refresh_token": login["refresh_token"]},
        )
        body = r.json()
        assert "access_token" in body
        assert isinstance(body["access_token"], str)
        assert len(body["access_token"]) > 20

    def test_refresh_returns_same_refresh_token(self, raw_client):
        """Refresh tokens are not rotated — same token returned."""
        login = raw_client.post(
            "/auth/token",
            data={"username": "admin", "password": "tracer-dev-password"},
        ).json()
        r = raw_client.post(
            "/auth/refresh",
            json={"refresh_token": login["refresh_token"]},
        )
        assert r.json()["refresh_token"] == login["refresh_token"]

    def test_access_token_cannot_be_used_to_refresh(self, raw_client):
        """Passing an access token to /refresh should fail — wrong type."""
        login = raw_client.post(
            "/auth/token",
            data={"username": "admin", "password": "tracer-dev-password"},
        ).json()
        r = raw_client.post(
            "/auth/refresh",
            json={"refresh_token": login["access_token"]},
        )
        assert r.status_code == 401

    def test_invalid_refresh_token_returns_401(self, raw_client):
        r = raw_client.post(
            "/auth/refresh",
            json={"refresh_token": "not.a.valid.token"},
        )
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# Current user endpoint
# ---------------------------------------------------------------------------

class TestMe:

    def test_me_with_valid_token_returns_200(self, client):
        r = client.get("/auth/me")
        assert r.status_code == 200

    def test_me_returns_username(self, client):
        r = client.get("/auth/me")
        assert r.json()["username"] == "admin"

    def test_me_without_token_returns_401(self, raw_client):
        r = raw_client.get("/auth/me")
        assert r.status_code == 401


# ---------------------------------------------------------------------------
# Protected route behaviour
# ---------------------------------------------------------------------------

class TestProtectedRoutes:

    def test_protected_route_without_token_returns_401(self, raw_client):
        r = raw_client.get("/node-types/")
        assert r.status_code == 401

    def test_protected_route_with_valid_token_returns_200(self, raw_client):
        login = raw_client.post(
            "/auth/token",
            data={"username": "admin", "password": "tracer-dev-password"},
        ).json()
        r = raw_client.get(
            "/node-types/",
            headers={"Authorization": f"Bearer {login['access_token']}"},
        )
        assert r.status_code == 200

    def test_protected_route_with_invalid_token_returns_401(self, raw_client):
        r = raw_client.get(
            "/node-types/",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert r.status_code == 401

    def test_protected_route_with_malformed_header_returns_401(self, raw_client):
        r = raw_client.get(
            "/node-types/",
            headers={"Authorization": "NotBearer sometoken"},
        )
        assert r.status_code == 401

    def test_health_check_is_public(self, raw_client):
        """GET / should always be accessible without a token."""
        r = raw_client.get("/")
        assert r.status_code == 200

    def test_login_endpoint_is_public(self, raw_client):
        """POST /auth/token must be accessible without a token."""
        r = raw_client.post(
            "/auth/token",
            data={"username": "admin", "password": "tracer-dev-password"},
        )
        assert r.status_code == 200

    def test_refresh_endpoint_is_public(self, raw_client):
        """POST /auth/refresh must be accessible without a token."""
        login = raw_client.post(
            "/auth/token",
            data={"username": "admin", "password": "tracer-dev-password"},
        ).json()
        r = raw_client.post(
            "/auth/refresh",
            json={"refresh_token": login["refresh_token"]},
        )
        assert r.status_code == 200
