from typing import List

from fastapi import APIRouter, status

from app.schemas.profile import ProfileCreate, ProfileResponse, ProfileUpdate
from app.services.profile_service import profile_service

router = APIRouter()


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(profile: ProfileCreate):
    """Create a new profile from structured resume JSON."""
    return await profile_service.create_profile(profile)


@router.get("/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: str):
    """Retrieve a profile by ID."""
    return await profile_service.get_profile(profile_id)


@router.patch("/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: str, profile_update: ProfileUpdate):
    """Partially update a profile."""
    return await profile_service.update_profile(profile_id, profile_update)


@router.get("/", response_model=List[ProfileResponse])
async def list_profiles(skip: int = 0, limit: int = 10):
    """List profiles with pagination."""
    return await profile_service.list_profiles(skip, limit)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: str):
    """Delete a profile."""
    await profile_service.delete_profile(profile_id)
