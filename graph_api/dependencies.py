"""
dependencies.py — shared FastAPI dependencies.

These are injected into route handlers via Depends().
Centralising them here means a single import rather than
repeating the logic across every router.

Usage in a router:
    from dependencies import get_current_user
    from schemas.auth import TokenData

    @router.get("/protected")
    def protected_route(current_user: TokenData = Depends(get_current_user)):
        return {"user": current_user.username}
"""
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from schemas.auth import TokenData
from services.auth_service import AuthError, decode_token

# ---------------------------------------------------------------------------
# OAuth2 bearer token scheme
# ---------------------------------------------------------------------------
# tokenUrl tells Swagger UI where to send the login form.
# It does not enforce anything — it is metadata for the docs only.

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Validate the Bearer token from the Authorization header.

    Raises AuthError (401) if the token is missing, expired, or invalid.
    Inject this into any route that requires authentication:

        @router.get("/")
        def my_route(user: TokenData = Depends(get_current_user)):
            ...
    """
    return decode_token(token, expected_type="access")
