"""
services/auth_service.py — JWT token creation and validation.

Keeps all JWT logic in one place so it is easy to audit and test.
The routers and dependencies call into here — they never touch
python-jose directly.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="passlib")
from passlib.context import CryptContext

from config import settings
from exceptions import TracerException
from schemas.auth import TokenData

# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plain: str) -> str:
    """Hash a plain-text password for storage."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if plain matches the stored hash."""
    return pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# Token creation
# ---------------------------------------------------------------------------

def _create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    """Internal helper — create a signed JWT with an expiry and type claim."""
    payload = data.copy()
    payload.update({
        "exp": datetime.now(timezone.utc) + expires_delta,
        "iat": datetime.now(timezone.utc),
        "type": token_type,
    })
    return jwt.encode(
        payload,
        settings.secret_key.get_secret_value(),
        algorithm=settings.algorithm,
    )


def create_access_token(username: str) -> str:
    """Create a short-lived access token."""
    return _create_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        token_type="access",
    )


def create_refresh_token(username: str) -> str:
    """Create a long-lived refresh token."""
    return _create_token(
        data={"sub": username},
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        token_type="refresh",
    )


# ---------------------------------------------------------------------------
# Token validation
# ---------------------------------------------------------------------------

class AuthError(TracerException):
    """Raised when a token is missing, expired, or invalid."""
    def __init__(self, message: str = "Could not validate credentials"):
        super().__init__(message=message, status_code=401)


def decode_token(token: str, expected_type: str = "access") -> TokenData:
    """
    Decode and validate a JWT.

    Args:
        token:         The raw JWT string from the Authorization header.
        expected_type: "access" or "refresh" — token must match.

    Returns:
        TokenData with the username extracted from the 'sub' claim.

    Raises:
        AuthError if the token is invalid, expired, or of the wrong type.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key.get_secret_value(),
            algorithms=[settings.algorithm],
        )
    except JWTError:
        raise AuthError("Token is invalid or has expired")

    username: Optional[str] = payload.get("sub")
    token_type: Optional[str] = payload.get("type")

    if username is None:
        raise AuthError("Token is missing subject claim")

    if token_type != expected_type:
        raise AuthError(f"Expected {expected_type} token, got {token_type}")

    return TokenData(username=username, token_type=token_type)


# ---------------------------------------------------------------------------
# User validation
# ---------------------------------------------------------------------------
#
# Phase 3 uses a single admin user configured via environment variables.
# To add multi-user support later:
#   1. Add ADMIN_USERNAME / ADMIN_PASSWORD_HASH to Settings in config.py
#   2. Update validate_credentials() to query the User table instead
#   3. Everything else (JWT structure, dependencies) stays the same
#
# For now the credentials are hardcoded for development. In production
# set ADMIN_USERNAME and ADMIN_PASSWORD_HASH in your .env file.

def validate_credentials(username: str, password: str) -> bool:
    """
    Validate login credentials.
    Returns True if the credentials match the configured admin user.
    """
    from config import settings as s

    # Read from settings — add ADMIN_USERNAME / ADMIN_PASSWORD to .env
    # to override these development defaults
    admin_username = getattr(s, "admin_username", "admin")
    admin_password = getattr(s, "admin_password", "tracer-dev-password")

    if username != admin_username:
        return False

    # In development the password is stored plain in .env for convenience.
    # In production set ADMIN_PASSWORD_HASH to a bcrypt hash and compare with
    # verify_password() instead.
    admin_password_hash = getattr(s, "admin_password_hash", None)
    if admin_password_hash:
        return verify_password(password, admin_password_hash)

    return password == admin_password
