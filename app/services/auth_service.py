"""
Authentication business logic.

Orchestrates user registration, login, token refresh, and password changes.
All password handling flows through the security module — plaintext passwords
never touch the database layer.
"""

import logging
from typing import Any, Dict, Tuple

from fastapi import HTTPException, status

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import user_repo
from app.schemas.auth import ChangePasswordRequest, UserLogin, UserRegister

logger = logging.getLogger(__name__)


class AuthService:
    """High-level authentication operations."""

    async def register(self, data: UserRegister) -> Tuple[Dict[str, Any], str, str]:
        """
        Register a new user.

        Returns (user_doc, access_token, refresh_token).
        Raises 409 if the email is already taken.
        """
        existing = await user_repo.find_by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )

        hashed = hash_password(data.password)
        user = await user_repo.create_user(data.name, data.email, hashed)

        access_token = create_access_token(subject=user["_id"])
        refresh_token = create_refresh_token(subject=user["_id"])

        logger.info("User registered: %s", data.email)
        return user, access_token, refresh_token

    async def login(self, data: UserLogin) -> Tuple[Dict[str, Any], str, str]:
        """
        Authenticate a user by email + password.

        Returns (user_doc, access_token, refresh_token).
        Raises 401 with a generic message to prevent email enumeration.
        """
        user = await user_repo.find_by_email(data.email)
        if not user or not verify_password(data.password, user["hashed_password"]):
            # Generic message — don't reveal whether email exists
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        access_token = create_access_token(subject=user["_id"])
        refresh_token = create_refresh_token(subject=user["_id"])

        logger.info("User logged in: %s", data.email)
        return user, access_token, refresh_token

    async def refresh(self, refresh_token_str: str) -> Tuple[str, str]:
        """
        Issue a new access + refresh token pair from a valid refresh token.

        Raises 401 if the refresh token is invalid or expired.
        """
        payload = decode_refresh_token(refresh_token_str)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )

        user_id = payload.get("sub")
        user = await user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        new_access = create_access_token(subject=user_id)
        new_refresh = create_refresh_token(subject=user_id)
        return new_access, new_refresh

    async def change_password(
        self, user_id: str, data: ChangePasswordRequest
    ) -> None:
        """
        Change the authenticated user's password.

        Verifies the current password before updating.
        """
        user = await user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(data.current_password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        new_hashed = hash_password(data.new_password)
        await user_repo.update_password(user_id, new_hashed)
        logger.info("Password changed for user: %s", user_id)

    @staticmethod
    def to_user_response(user: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a raw user document to the public-safe response shape."""
        return {
            "id": user["_id"],
            "name": user["name"],
            "email": user["email"],
            "created_at": user.get("created_at"),
        }


auth_service = AuthService()
