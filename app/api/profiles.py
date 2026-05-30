"""
Profile CRUD endpoints — all protected by authentication.

Every request requires a valid access_token cookie.  Profiles are scoped
to the authenticated user.
"""

from typing import List

from fastapi import APIRouter, status

from app.core.dependencies import CurrentUser
from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.profile_service import profile_service

router = APIRouter()


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile: ProfileCreate, user: CurrentUser):
    """Create a new profile owned by the current user."""
    return await profile_service.create_profile(profile, user_id=user["_id"])


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: str, user: CurrentUser):
    """Retrieve a profile by ID (ownership verified)."""
    return await profile_service.get_profile(profile_id, user_id=user["_id"])


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: str, profile_update: ProfileUpdate, user: CurrentUser):
    """Partially update a profile (ownership verified)."""
    return await profile_service.update_profile(profile_id, profile_update, user_id=user["_id"])


@router.get("/", response_model=List[ProfileResponse])
async def list_profiles(skip: int = 0, limit: int = 10, user: CurrentUser = None):
    """List the current user's profiles with pagination."""
    return await profile_service.list_profiles(user_id=user["_id"], skip=skip, limit=limit)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: str, user: CurrentUser):
    """Delete a profile (ownership verified)."""
    await profile_service.delete_profile(profile_id, user_id=user["_id"])
