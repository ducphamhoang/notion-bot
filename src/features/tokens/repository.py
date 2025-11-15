"""Repository for Notion API token CRUD operations."""

import logging
from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from bson.errors import InvalidId

from src.core.database.connection import DatabaseConnection
from src.features.tokens.models import NotionToken
from src.core.errors.exceptions import NotFoundError, InternalError

logger = logging.getLogger(__name__)


class TokenRepository:
    """Repository for managing Notion API tokens in MongoDB."""

    def __init__(self, database: Optional[AsyncIOMotorDatabase] = None):
        """Initialize repository with optional database injection.
        
        Args:
            database: Optional database for testing. Defaults to production database if not provided.
        """
        self._database = database

    @property
    async def collection(self):
        """Get the tokens collection from database."""
        if self._database is None:
            db_connection = DatabaseConnection()
            self._database = await db_connection.get_database()
        return self._database["tokens"]

    async def create(self, token_data: dict) -> NotionToken:
        """Create a new token in the database.
        
        Args:
            token_data: Dictionary containing token fields
            
        Returns:
            Created NotionToken instance
            
        Raises:
            InternalError: If database operation fails
        """
        try:
            token_data["created_at"] = datetime.utcnow()
            token_data["updated_at"] = datetime.utcnow()
            
            collection = await self.collection
            result = await collection.insert_one(token_data)
            
            token_data["_id"] = result.inserted_id
            logger.info(f"Created token with ID: {result.inserted_id}, name: {token_data.get('name')}")
            
            return NotionToken(**token_data)
        except Exception as e:
            logger.error(f"Failed to create token: {str(e)}")
            raise InternalError("Failed to create token", original_error=e)

    async def get_by_id(self, token_id: str) -> NotionToken:
        """Get token by ID.
        
        Args:
            token_id: String representation of ObjectId
            
        Returns:
            NotionToken instance
            
        Raises:
            NotFoundError: If token ID is invalid or token doesn't exist
        """
        try:
            obj_id = ObjectId(token_id)
        except (InvalidId, ValueError) as e:
            logger.warning(f"Invalid token ID format: {token_id}")
            raise NotFoundError(entity_type="Token", entity_id=token_id)

        try:
            collection = await self.collection
            token_doc = await collection.find_one({"_id": obj_id})
            
            if not token_doc:
                raise NotFoundError(entity_type="Token", entity_id=token_id)
            
            return NotionToken(**token_doc)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to get token {token_id}: {str(e)}")
            raise InternalError(f"Failed to retrieve token", original_error=e)

    async def list_all(self, active_only: bool = True) -> List[NotionToken]:
        """List all tokens with optional active filter.
        
        Args:
            active_only: If True, only return active tokens
            
        Returns:
            List of NotionToken instances
            
        Raises:
            InternalError: If database operation fails
        """
        try:
            collection = await self.collection
            query = {"is_active": True} if active_only else {}
            
            cursor = collection.find(query).sort("created_at", -1)
            tokens = []
            
            async for token_doc in cursor:
                tokens.append(NotionToken(**token_doc))
            
            logger.info(f"Listed {len(tokens)} tokens (active_only={active_only})")
            return tokens
        except Exception as e:
            logger.error(f"Failed to list tokens: {str(e)}")
            raise InternalError("Failed to list tokens", original_error=e)

    async def update(self, token_id: str, updates: dict) -> NotionToken:
        """Update token fields.
        
        Args:
            token_id: String representation of ObjectId
            updates: Dictionary of fields to update
            
        Returns:
            Updated NotionToken instance
            
        Raises:
            NotFoundError: If token doesn't exist
            InternalError: If database operation fails
        """
        try:
            obj_id = ObjectId(token_id)
        except (InvalidId, ValueError):
            raise NotFoundError(entity_type="Token", entity_id=token_id)

        try:
            updates["updated_at"] = datetime.utcnow()
            
            collection = await self.collection
            result = await collection.find_one_and_update(
                {"_id": obj_id},
                {"$set": updates},
                return_document=True
            )
            
            if not result:
                raise NotFoundError(entity_type="Token", entity_id=token_id)
            
            logger.info(f"Updated token {token_id}")
            return NotionToken(**result)
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to update token {token_id}: {str(e)}")
            raise InternalError(f"Failed to update token", original_error=e)

    async def delete(self, token_id: str) -> bool:
        """Delete token by ID.
        
        Args:
            token_id: String representation of ObjectId
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundError: If token doesn't exist
            InternalError: If database operation fails
        """
        try:
            obj_id = ObjectId(token_id)
        except (InvalidId, ValueError):
            raise NotFoundError(entity_type="Token", entity_id=token_id)

        try:
            collection = await self.collection
            result = await collection.delete_one({"_id": obj_id})
            
            if result.deleted_count == 0:
                raise NotFoundError(entity_type="Token", entity_id=token_id)
            
            logger.info(f"Deleted token {token_id}")
            return True
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete token {token_id}: {str(e)}")
            raise InternalError(f"Failed to delete token", original_error=e)

    async def get_token_value(self, token_id: str) -> str:
        """Get raw token string for Notion API calls.
        
        Args:
            token_id: String representation of ObjectId
            
        Returns:
            Raw token value
            
        Raises:
            NotFoundError: If token doesn't exist
        """
        token = await self.get_by_id(token_id)
        return token.token
