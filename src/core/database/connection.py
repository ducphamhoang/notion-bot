"""MongoDB connection management with pooling and retry logic."""

import asyncio
import logging
from typing import AsyncGenerator, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from src.config.settings import get_settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages MongoDB connection with connection pooling and retry logic."""
    
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None
    _connection_lock = asyncio.Lock()
    
    @classmethod
    async def get_client(cls) -> AsyncIOMotorClient:
        """Get MongoDB client instance, creating if needed."""
        if cls._client is None:
            async with cls._connection_lock:
                if cls._client is None:
                    settings = get_settings()
                    logger.info(f"Connecting to MongoDB at {settings.mongodb_uri}")
                    
                    cls._client = AsyncIOMotorClient(
                        settings.mongodb_uri,
                        maxPoolSize=10,
                        minPoolSize=2,
                        retryWrites=True,
                        retryReads=True,
                        serverSelectionTimeoutMS=5000,
                        connectTimeoutMS=5000,
                        socketTimeoutMS=30000,
                    )
                    
                    # Test connection
                    await cls._client.admin.command('ping')
                    logger.info("Successfully connected to MongoDB")
        
        return cls._client
    
    @classmethod
    async def get_database(cls) -> AsyncIOMotorDatabase:
        """Get MongoDB database instance."""
        if cls._database is None:
            client = await cls.get_client()
            # Extract database name from connection URI or use default
            settings = get_settings()
            db_name = settings.mongodb_uri.split('/')[-1] or 'notion-bot'
            cls._database = client[db_name]
        
        return cls._database
    
    @classmethod
    async def close_connection(cls) -> None:
        """Close MongoDB connection."""
        if cls._client is not None:
            cls._client.close()
            cls._client = None
            cls._database = None
            logger.info("MongoDB connection closed")
    
    @classmethod
    async def health_check(cls) -> dict:
        """Check MongoDB connectivity and return health status."""
        try:
            client = await cls.get_client()
            db = await cls.get_database()
            
            # Simple ping test
            result = await db.command('ping')
            
            return {
                "status": "healthy",
                "mongodb": {
                    "status": "connected",
                    "ping": result
                }
            }
        except Exception as e:
            logger.error(f"MongoDB health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "mongodb": {
                    "status": "disconnected",
                    "error": str(e)
                }
            }


# Dependency injection helper
async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency to get database instance."""
    return await DatabaseConnection.get_database()
