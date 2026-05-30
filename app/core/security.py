"""
Security utilities — password hashing, JWT tokens, and cookie management.

All secrets are loaded from the centralised Settings object.
"""

import bcrypt
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError
from fastapi import Response

from app.core.config import settings

# ── Password hashing (bcrypt) ────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Return a bcrypt hash of the plaintext password."""
    # bcrypt.hashpw returns bytes, so we decode to string for storage
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )


# ── JWT token creation ───────────────────────────────────────────────────
def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Create a short-lived JWT access token.

    The `sub` claim holds the user ID (as string).
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {"sub": subject, "exp": expire, "type": "access"}
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")


def create_refresh_token(subject: str, expires_delta: timedelta | None = None) -> str:
    """
    Create a long-lived JWT refresh token.

    Uses a *separate* secret so a leaked access-token secret cannot be used
    to forge refresh tokens.
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(to_encode, settings.JWT_REFRESH_SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> dict | None:
    """Decode and validate an access token.  Returns payload or None."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> dict | None:
    """Decode and validate a refresh token.  Returns payload or None."""
    try:
        payload = jwt.decode(token, settings.JWT_REFRESH_SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None


# ── Cookie helpers ───────────────────────────────────────────────────────
# Using HttpOnly + SameSite=Lax cookies prevents XSS-based token theft
# and provides CSRF protection for same-site requests.

def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    """Set access and refresh tokens as secure HttpOnly cookies."""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,          # JS cannot read this cookie
        samesite="lax",         # CSRF protection for same-origin
        secure=False,           # Set True in production (HTTPS)
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,           # Set True in production (HTTPS)
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    """Remove auth cookies from the client."""
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/")
