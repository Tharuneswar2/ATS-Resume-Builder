from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from pymongo import ReturnDocument

from app.core.database import get_db
from app.schemas.profile import ProfileCreate, ProfileUpdate


class ProfileRepository:
    def __init__(self):
        self.collection_name = "profiles"

    @property
    def collection(self):
        return get_db()[self.collection_name]

    def _to_object_id(self, profile_id: str) -> Optional[ObjectId]:
        try:
            return ObjectId(profile_id)
        except (InvalidId, TypeError):
            return None

    async def create_profile(self, profile_data: ProfileCreate, user_id: str) -> Dict[str, Any]:
        """Create a profile document owned by the given user."""
        document = profile_data.model_dump()
        document["user_id"] = user_id  # Ownership field
        result = await self.collection.insert_one(document)
        document["_id"] = str(result.inserted_id)
        return document

    async def get_profile(self, profile_id: str) -> Optional[Dict[str, Any]]:
        object_id = self._to_object_id(profile_id)
        if object_id is None:
            return None
        document = await self.collection.find_one({"_id": object_id})
        if document:
            document["_id"] = str(document["_id"])
        return document

    async def update_profile(self, profile_id: str, profile_data: ProfileUpdate) -> Optional[Dict[str, Any]]:
        object_id = self._to_object_id(profile_id)
        if object_id is None:
            return None
        update_data = {k: v for k, v in profile_data.model_dump(exclude_unset=True).items() if v is not None}
        if not update_data:
            return await self.get_profile(profile_id)

        result = await self.collection.find_one_and_update(
            {"_id": object_id},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER,
        )
        if result:
            result["_id"] = str(result["_id"])
        return result

    async def list_profiles(self, user_id: str, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """List profiles filtered by the owning user_id."""
        cursor = self.collection.find({"user_id": user_id}).skip(skip).limit(limit)
        documents = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            documents.append(doc)
        return documents

    async def delete_profile(self, profile_id: str) -> bool:
        object_id = self._to_object_id(profile_id)
        if object_id is None:
            return False
        result = await self.collection.delete_one({"_id": object_id})
        return result.deleted_count > 0


profile_repo = ProfileRepository()
