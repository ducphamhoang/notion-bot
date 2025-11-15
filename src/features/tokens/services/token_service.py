"""Service layer for Notion API token management."""

import logging
from typing import Optional

from src.features.tokens.repository import TokenRepository
from src.features.tokens.dto.create_token_request import CreateTokenRequest
from src.features.tokens.dto.update_token_request import UpdateTokenRequest
from src.features.tokens.dto.token_response import TokenResponse
from src.features.tokens.dto.token_list_response import TokenListResponse
from src.core.errors.exceptions import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


class TokenService:
    """Service for managing Notion API tokens."""

    def __init__(self, repository: Optional[TokenRepository] = None):
        """Initialize service with optional repository injection for testability.
        
        Args:
            repository: Optional repository for testing. Defaults to production repository if not provided.
        """
        self._repository = repository or TokenRepository()

    async def create_token(self, request: CreateTokenRequest) -> TokenResponse:
        """Create a new Notion API token.
        
        Args:
            request: Token creation request data
            
        Returns:
            TokenResponse with masked token value
            
        Raises:
            ValidationError: If token format is invalid
        """
        token_data = {
            "name": request.name,
            "token": request.token,
            "description": request.description,
            "is_active": True
        }
        
        logger.info(f"Creating new token: {request.name}")
        token = await self._repository.create(token_data)
        
        return TokenResponse.from_token(token, self.mask_token)

    async def list_tokens(self, active_only: bool = True) -> TokenListResponse:
        """List all Notion API tokens.
        
        Args:
            active_only: If True, only return active tokens
            
        Returns:
            TokenListResponse with masked token values
        """
        logger.info(f"Listing tokens (active_only={active_only})")
        tokens = await self._repository.list_all(active_only=active_only)
        
        token_responses = [
            TokenResponse.from_token(token, self.mask_token)
            for token in tokens
        ]
        
        return TokenListResponse(
            tokens=token_responses,
            total=len(token_responses)
        )

    async def get_token(self, token_id: str) -> TokenResponse:
        """Get a single Notion API token by ID.
        
        Args:
            token_id: Token ID to retrieve
            
        Returns:
            TokenResponse with masked token value
            
        Raises:
            NotFoundError: If token doesn't exist
        """
        logger.info(f"Getting token: {token_id}")
        token = await self._repository.get_by_id(token_id)
        
        return TokenResponse.from_token(token, self.mask_token)

    async def update_token(self, token_id: str, request: UpdateTokenRequest) -> TokenResponse:
        """Update an existing Notion API token.
        
        Args:
            token_id: Token ID to update
            request: Token update request data
            
        Returns:
            TokenResponse with masked token value
            
        Raises:
            NotFoundError: If token doesn't exist
        """
        from typing import Any, Dict
        updates: Dict[str, Any] = {}
        if request.name is not None:
            updates["name"] = request.name
        if request.description is not None:
            updates["description"] = request.description
        if request.is_active is not None:
            updates["is_active"] = request.is_active
        
        if not updates:
            raise ValidationError("No fields to update", field="body")
        
        logger.info(f"Updating token: {token_id} with fields: {list(updates.keys())}")
        token = await self._repository.update(token_id, updates)
        
        return TokenResponse.from_token(token, self.mask_token)

    async def delete_token(self, token_id: str) -> None:
        """Delete a Notion API token.
        
        Args:
            token_id: Token ID to delete
            
        Raises:
            NotFoundError: If token doesn't exist
        """
        logger.info(f"Deleting token: {token_id}")
        await self._repository.delete(token_id)

    @staticmethod
    def mask_token(raw_token: str) -> str:
        """Mask a token value, showing only last 6 characters.
        
        Args:
            raw_token: Raw token value to mask
            
        Returns:
            Masked token in format "******...abc123"
        """
        if len(raw_token) <= 6:
            return "******"
        
        last_six = raw_token[-6:]
        return f"******...{last_six}"
