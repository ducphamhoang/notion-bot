"""Repository for user mapping operations."""

from datetime import datetime
from typing import Optional
import logging
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ASCENDING

from src.core.database.connection import DatabaseConnection
from src.features.users.models import UserMapping, UserMappingInDB


logger = logging.getLogger(__name__)


class UserMappingRepository:
    """Repository for user mapping database operations."""

    def __init__(self, db_connection: DatabaseConnection = None):
        """Initialize repository."""
        self._db_connection = db_connection or DatabaseConnection()

    async def get_collection(self) -> AsyncIOMotorCollection:
        """Get the user_mappings collection."""
        db = await self._db_connection.get_database()
        return db["user_mappings"]

    async def create_indexes(self) -> None:
        """Create required indexes for the collection."""
        collection = await self.get_collection()
        
        # Create index on platform and platform_user_id for fast lookups
        await collection.create_index([
            ("platform", ASCENDING),
            ("platform_user_id", ASCENDING)
        ], unique=True)

    async def create_mapping(self, mapping: UserMapping) -> UserMappingInDB:
        """Create a new user mapping."""
        collection = await self.get_collection()
        
        mapping.updated_at = datetime.utcnow()
        if not mapping.created_at:
            mapping.created_at = datetime.utcnow()
        
        result = await collection.insert_one(mapping.dict(by_alias=True))
        
        # Return the created mapping with the generated ID
        mapping.id = result.inserted_id
        return UserMappingInDB(**mapping.dict(by_alias=True))

    async def find_by_platform_and_user_id(
        self, 
        platform: str, 
        platform_user_id: str
    ) -> Optional[UserMappingInDB]:
        """Find a user mapping by platform and platform user ID."""
        collection = await self.get_collection()
        
        document = await collection.find_one({
            "platform": platform,
            "platform_user_id": platform_user_id
        })
        
        if document:
            return UserMappingInDB(**document)
        
        return None

    async def find_by_id(self, mapping_id: str) -> Optional[UserMappingInDB]:
        """Find a user mapping by its database ID."""
        from bson import ObjectId
        
        collection = await self.get_collection()
        
        document = await collection.find_one({"_id": ObjectId(mapping_id)})
        
        if document:
            return UserMappingInDB(**document)
        
        return None

    async def update_mapping(self, mapping_id: str, mapping: UserMapping) -> Optional[UserMappingInDB]:
        """Update an existing user mapping."""
        from bson import ObjectId
        
        collection = await self.get_collection()
        
        mapping.updated_at = datetime.utcnow()
        result = await collection.update_one(
            {"_id": ObjectId(mapping_id)},
            {"$set": mapping.dict(exclude={"id", "_id"}, by_alias=True)}
        )
        
        if result.matched_count == 0:
            return None
        
        # Return the updated mapping
        return await self.find_by_id(mapping_id)

    async def delete_mapping(self, mapping_id: str) -> bool:
        """Delete a user mapping by its database ID."""
        from bson import ObjectId

        collection = await self.get_collection()

        result = await collection.delete_one({"_id": ObjectId(mapping_id)})
        return result.deleted_count > 0

    async def list_mappings(
        self,
        platform: Optional[str] = None,
        platform_user_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[list[UserMappingInDB], int]:
        """List user mappings with optional filtering and pagination."""
        collection = await self.get_collection()

        # Build query based on filters
        query = {}
        if platform:
            query["platform"] = platform
        if platform_user_id:
            query["platform_user_id"] = platform_user_id

        # Get total count
        total = await collection.count_documents(query)

        # Get paginated results
        cursor = collection.find(query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)

        mappings = [UserMappingInDB(**doc) for doc in documents]

        return mappings, total