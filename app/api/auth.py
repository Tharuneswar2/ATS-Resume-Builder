"""
Authentication API endpoints.

All token storage is via HttpOnly cookies — no tokens in response bodies.
Includes a simple in-memory rate limiter on login to mitigate brute-force.
"""

import time
import logging
from collections import defaultdict

from fastapi import APIRouter, HTTPException, Request, Response, status

from app.core.dependencies import CurrentUser
from app.core.security import clear_auth_cookies, set_auth_cookies
from app.schemas.auth import (
    ChangePasswordRequest,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.services.auth_service import auth_service

logger = logging.getLogger(__name__)
router = APIRouter()

# ── Simple in-memory rate limiter ────────────────────────────────────────
# Tracks login attempts per IP.  Max 10 attempts per 60-second window.
_login_attempts: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_MAX = 10
_RATE_LIMIT_WINDOW = 60  # seconds


def _check_rate_limit(ip: str) -> None:
    """Raise 429 if the IP has exceeded the login attempt threshold."""
    now = time.time()
    # Prune old entries
    _login_attempts[ip] = [t for t in _login_attempts[ip] if now - t < _RATE_LIMIT_WINDOW]
    if len(_login_attempts[ip]) >= _RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )
    _login_attempts[ip].append(now)


# ── Endpoints ────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, response: Response):
    """Create a new user account and set auth cookies."""
    user, access_token, refresh_token = await auth_service.register(data)
    set_auth_cookies(response, access_token, refresh_token)
    return auth_service.to_user_response(user)


@router.post("/login", response_model=UserResponse)
async def login(data: UserLogin, request: Request, response: Response):
    """Authenticate and set auth cookies.  Rate-limited by IP."""
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    user, access_token, refresh_token = await auth_service.login(data)
    set_auth_cookies(response, access_token, refresh_token)
    return auth_service.to_user_response(user)


@router.post("/logout")
async def logout(response: Response):
    """Clear auth cookies to log the user out."""
    clear_auth_cookies(response)
    return {"detail": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(user: CurrentUser):
    """Return the currently authenticated user's profile."""
    return auth_service.to_user_response(user)


@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    """
    Issue a new access token using the refresh token cookie.

    The client calls this when a 401 is received on a protected route.
    """
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token",
        )

    new_access, new_refresh = await auth_service.refresh(token)
    set_auth_cookies(response, new_access, new_refresh)
    return {"detail": "Token refreshed"}


@router.post("/change-password")
async def change_password(data: ChangePasswordRequest, user: CurrentUser):
    """Change the authenticated user's password."""
    await auth_service.change_password(user["_id"], data)
    return {"detail": "Password changed successfully"}
