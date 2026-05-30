"""
MongoDB repository for the `users` collection.

Handles all direct database operations for user accounts.
A unique index on `email` ensures no duplicate registrations.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from bson import ObjectId
from bson.errors import InvalidId

from app.core.database import get_db

logger = logging.getLogger(__name__)


class UserRepository:
    """CRUD operations on the `users` MongoDB collection."""

    def __init__(self):
        self.collection_name = "users"
        self._index_created = False

    @property
    def collection(self):
        return get_db()[self.collection_name]

    async def _ensure_indexes(self) -> None:
        """Create a unique index on email (idempotent)."""
        if not self._index_created:
            await self.collection.create_index("email", unique=True)
            self._index_created = True

    def _to_object_id(self, user_id: str) -> Optional[ObjectId]:
        try:
            return ObjectId(user_id)
        except (InvalidId, TypeError):
            return None

    @staticmethod
    def _sanitize(doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert ObjectId to string and strip the hashed_password."""
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def create_user(self, name: str, email: str, hashed_password: str) -> Dict[str, Any]:
        """
        Insert a new user document.

        The password is already hashed before reaching this layer.
        """
        await self._ensure_indexes()
        document = {
            "name": name,
            "email": email.lower(),
            "hashed_password": hashed_password,
            "created_at": datetime.now(timezone.utc),
        }
        result = await self.collection.insert_one(document)
        document["_id"] = str(result.inserted_id)
        return document

    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find a user by email address (case-insensitive)."""
        await self._ensure_indexes()
        doc = await self.collection.find_one({"email": email.lower()})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def find_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find a user by their MongoDB ObjectId string."""
        oid = self._to_object_id(user_id)
        if oid is None:
            return None
        doc = await self.collection.find_one({"_id": oid})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def update_password(self, user_id: str, hashed_password: str) -> bool:
        """Update a user's hashed password."""
        oid = self._to_object_id(user_id)
        if oid is None:
            return False
        result = await self.collection.update_one(
            {"_id": oid},
            {"$set": {"hashed_password": hashed_password}},
        )
        return result.modified_count > 0


user_repo = UserRepository()
