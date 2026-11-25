from typing import Any, Optional
import motor.motor_asyncio
from core.config import settings
import logging

logger = logging.getLogger(__name__)

# Fallback to localhost if MONGO_URL not provided
mongo_url = settings.MONGO_URL or "mongodb://localhost:27017"
mongo_client: Optional[Any] = None
mongo_db: Optional[Any] = None
try:
    mongo_client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url, serverSelectionTimeoutMS=2000)
    mongo_db = mongo_client["vireoniq"]
    logger.info(f"Initialized Mongo client with URL: {mongo_url}")
except Exception as e:
    logger.error(f"Failed to initialize MongoDB client: {e}")
    mongo_db = None
