"""
FastAPI dependencies for authentication.

Provides `get_current_user` which extracts the JWT from the HttpOnly cookie,
validates it, and returns the user document from MongoDB.
"""

from typing import Annotated, Any, Dict

from fastapi import Depends, HTTPException, Request, status

from app.core.security import decode_access_token
from app.repositories.user_repository import user_repo


async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Dependency that extracts the current authenticated user.

    Reads the `access_token` cookie, decodes the JWT, and fetches the
    user from MongoDB.  Raises 401 if the token is missing, expired,
    or the user no longer exists.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await user_repo.find_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# Convenience type alias — use in route signatures:
#   async def my_route(user: CurrentUser):
CurrentUser = Annotated[Dict[str, Any], Depends(get_current_user)]
