"""
schemas/auth.py — Pydantic models for authentication.

For Phase 3 Tracer uses a simple single-user model — one set of
credentials configured via environment variables. This is appropriate
for a personal/small-team tool and avoids the complexity of a full
User table and registration flow.

When the commercial path requires multi-user support, add a User model
and update the auth service to validate against the database instead
of environment variables. The JWT structure and all dependent code
stays the same.
"""
from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    """Credentials submitted to POST /auth/token."""
    username: str
    password: str


class Token(BaseModel):
    """Returned on successful login."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int           # access token lifetime in seconds


class RefreshRequest(BaseModel):
    """Body for POST /auth/refresh."""
    refresh_token: str


class TokenData(BaseModel):
    """
    Decoded payload of a validated JWT.
    Used internally by get_current_user — not returned to clients.
    """
    username: Optional[str] = None
    token_type: Optional[str] = None  # "access" | "refresh"
