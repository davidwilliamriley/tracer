"""
routers/auth.py — authentication endpoints.

POST /auth/token   — login with username/password, receive JWT tokens
POST /auth/refresh — exchange a refresh token for a new access token
GET  /auth/me      — return the currently authenticated user (useful for
                     frontend to verify a stored token is still valid)
"""
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from config import settings
from dependencies import get_current_user
from exceptions import TracerException
from schemas.auth import LoginRequest, RefreshRequest, Token, TokenData
from services.auth_service import (
    AuthError,
    create_access_token,
    create_refresh_token,
    decode_token,
    validate_credentials,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with username and password, receive access and refresh tokens.

    Uses OAuth2PasswordRequestForm so Swagger UI's 'Authorize' button works
    out of the box — click it, enter credentials, and all subsequent requests
    in the docs will include the token automatically.

    The access token is short-lived (default 60 minutes).
    The refresh token is long-lived (default 7 days).
    """
    if not validate_credentials(form_data.username, form_data.password):
        raise AuthError("Incorrect username or password")

    return Token(
        access_token=create_access_token(form_data.username),
        refresh_token=create_refresh_token(form_data.username),
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=Token)
def refresh(body: RefreshRequest):
    """
    Exchange a valid refresh token for a new access token.

    Call this when the access token expires rather than asking the user
    to log in again. The refresh token itself is not rotated — it remains
    valid until it expires naturally.
    """
    token_data = decode_token(body.refresh_token, expected_type="refresh")

    return Token(
        access_token=create_access_token(token_data.username),
        refresh_token=body.refresh_token,  # return same refresh token
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=dict)
def get_me(current_user: TokenData = Depends(get_current_user)):
    """
    Return the currently authenticated user.
    Useful for the frontend to verify a stored token is still valid
    on app startup without making a full API call.
    """
    return {"username": current_user.username}
