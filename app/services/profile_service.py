"""
Profile service with user ownership enforcement.

Every profile is scoped to a user — the service layer verifies that the
authenticated user owns the profile before allowing reads, updates, or deletes.
"""

from typing import Any, Dict, List

from fastapi import HTTPException, status

from app.repositories.profile_repository import profile_repo
from app.schemas.profile import ProfileCreate, ProfileUpdate


class ProfileService:
    async def create_profile(self, profile: ProfileCreate, user_id: str) -> Dict[str, Any]:
        """Create and persist a profile document owned by `user_id`."""
        return await profile_repo.create_profile(profile, user_id)

    async def get_profile(self, profile_id: str, user_id: str) -> Dict[str, Any]:
        """Return a profile by ID, verifying ownership."""
        profile = await profile_repo.get_profile(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        # Ownership check — prevent access to other users' profiles
        if profile.get("user_id") and profile["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this profile",
            )
        return profile

    async def update_profile(self, profile_id: str, profile_update: ProfileUpdate, user_id: str) -> Dict[str, Any]:
        """Apply a partial profile update after verifying ownership."""
        # First check ownership
        await self.get_profile(profile_id, user_id)
        profile = await profile_repo.update_profile(profile_id, profile_update)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile

    async def list_profiles(self, user_id: str, skip: int = 0, limit: int = 10) -> List[Dict[str, Any]]:
        """List profile documents belonging to `user_id` with pagination."""
        return await profile_repo.list_profiles(user_id=user_id, limit=limit, skip=skip)

    async def delete_profile(self, profile_id: str, user_id: str) -> bool:
        """Delete a profile after verifying ownership."""
        await self.get_profile(profile_id, user_id)
        success = await profile_repo.delete_profile(profile_id)
        if not success:
            raise HTTPException(status_code=404, detail="Profile not found")
        return True


profile_service = ProfileService()
