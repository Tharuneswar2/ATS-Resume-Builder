from typing import Any, Dict, List

from fastapi import HTTPException

from app.repositories.profile_repository import profile_repo
from app.schemas.profile import ProfileCreate, ProfileUpdate


class ProfileService:
    async def create_profile(self, profile: ProfileCreate) -> Dict[str, Any]:
        """Create and persist a profile document."""
        return await profile_repo.create_profile(profile)

    async def get_profile(self, profile_id: str) -> Dict[str, Any]:
        """Return a profile by ID or raise 404."""
        profile = await profile_repo.get_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile

    async def update_profile(self, profile_id: str, profile_update: ProfileUpdate) -> Dict[str, Any]:
        """Apply a partial profile update."""
        profile = await profile_repo.update_profile(profile_id, profile_update)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile

    async def list_profiles(self, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """List profile documents with pagination."""
        return await profile_repo.list_profiles(limit=limit, skip=skip)

    async def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile or raise 404."""
        success = await profile_repo.delete_profile(profile_id)
        if not success:
            raise HTTPException(status_code=404, detail="Profile not found")
        return True


profile_service = ProfileService()
