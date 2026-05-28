"""
Async MongoDB connection manager (Motor).

Provides module-level helpers to connect, disconnect, and access the database
object throughout the application lifecycle.
"""

import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Module-level state
# ---------------------------------------------------------------------------
class _DatabaseState:
    """Thin wrapper to keep a reference to the Motor client + database."""
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None


_state = _DatabaseState()


# ---------------------------------------------------------------------------
# Lifecycle helpers (called from the FastAPI lifespan context)
# ---------------------------------------------------------------------------
async def connect_to_mongo() -> None:
    """Open the Motor client and select the configured database."""
    logger.info("Connecting to MongoDB at %s …", settings.MONGODB_URL)
    _state.client = AsyncIOMotorClient(settings.MONGODB_URL)
    _state.db = _state.client[settings.DATABASE_NAME]
    logger.info("Connected — database: %s", settings.DATABASE_NAME)


async def close_mongo_connection() -> None:
    """Gracefully shut down the Motor client."""
    if _state.client:
        _state.client.close()
        logger.info("MongoDB connection closed.")


# ---------------------------------------------------------------------------
# Accessor
# ---------------------------------------------------------------------------
def get_db() -> AsyncIOMotorDatabase:
    """Return the active database handle.  Raises if called before connect."""
    if _state.db is None:
        raise RuntimeError(
            "Database is not initialised.  "
            "Ensure the application lifespan has started."
        )
    return _state.db
