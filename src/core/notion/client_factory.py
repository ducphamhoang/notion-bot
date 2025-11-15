"""Factory for creating Notion clients with token resolution."""

import logging
from typing import Optional

from notion_client import AsyncClient

from src.config.settings import get_settings
from src.core.database.connection import DatabaseConnection
from src.features.tokens.repository import TokenRepository
from src.core.errors.exceptions import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class NotionClientFactory:
    """Factory for creating Notion API clients with token resolution."""

    @staticmethod
    async def create_client(token_id: Optional[str] = None) -> AsyncClient:
        """Create a Notion API client with optional token selection.
        
        Args:
            token_id: Optional token ID to use. If None, uses NOTION_API_KEY from environment.
            
        Returns:
            Configured AsyncClient instance
            
        Raises:
            NotFoundError: If token_id is provided but token doesn't exist
            ValidationError: If token exists but is inactive
        """
        settings = get_settings()
        api_key: str
        
        if token_id:
            # Resolve token from database
            logger.info(f"Resolving Notion client with token_id: {token_id}")
            
            # Get database connection using pattern from workspace routes
            db_connection = DatabaseConnection()
            database = await db_connection.get_database()
            
            # Create repository and get token
            repository = TokenRepository(database)
            token = await repository.get_by_id(token_id)
            
            # Validate token is active
            if not token.is_active:
                logger.warning(f"Attempted to use inactive token: {token_id}")
                raise ValidationError(
                    message=f"Token '{token.name}' is inactive and cannot be used",
                    field="token_id"
                )
            
            api_key = token.token
            logger.info(f"Using token '{token.name}' (ID: {token_id}) for Notion client")
        else:
            # Fallback to environment variable
            logger.info("Using NOTION_API_KEY from environment for Notion client")
            api_key = settings.notion_api_key
        
        # Create and return Notion client
        return AsyncClient(
            auth=api_key,
            notion_version=settings.notion_api_version
        )
