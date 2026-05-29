import logging

from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorDatabase

from app.core.config import settings

logger = logging.getLogger(__name__)

class _DatabaseState:
    client: AsyncIOMotorClient | None = None
    db: AsyncIOMotorDatabase | None = None
    
    
_state = _DatabaseState()


async def connect_to_mongo() -> None:
    """Open the Motor client and select the configured database."""
    logger.info("Connecting to MongoDB at %s …", settings.MONGODB_URL)
    _state.client = AsyncIOMotorClient(settings.MONGODB_URL)
    _state.db = _state.client[settings.DATABASE_NAME]
    logger.info("Connected — database: %s", settings.DATABASE_NAME)
    
    
async def close_mongo_connection() -> None:
    """Close the Motor client."""
    if _state.client:
        _state.client.close()
        logger.info("MongoDB connection closed.")