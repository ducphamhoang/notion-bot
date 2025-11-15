"""API routes for Notion API token management."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import Response

from src.core.database.connection import DatabaseConnection
from src.features.tokens.dto.create_token_request import CreateTokenRequest
from src.features.tokens.dto.update_token_request import UpdateTokenRequest
from src.features.tokens.dto.token_response import TokenResponse
from src.features.tokens.dto.token_list_response import TokenListResponse
from src.features.tokens.repository import TokenRepository
from src.features.tokens.services.token_service import TokenService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tokens", tags=["tokens"])


async def get_token_service() -> TokenService:
    """Dependency injection for token service."""
    db_connection = DatabaseConnection()
    repository = TokenRepository(await db_connection.get_database())
    return TokenService(repository=repository)


@router.post(
    "/",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new Notion API token",
    description="Store a new Notion API token for use in task operations."
)
async def create_token(
    request: CreateTokenRequest,
    token_service: Annotated[TokenService, Depends(get_token_service)]
) -> TokenResponse:
    """
    Create a new Notion API token.
    
    - **name**: Human-readable token name (1-100 chars)
    - **token**: Raw Notion API token (must start with 'secret_')
    - **description**: Optional token description
    
    Returns the created token with masked value.
    """
    return await token_service.create_token(request)


@router.get(
    "/",
    response_model=TokenListResponse,
    summary="List all Notion API tokens",
    description="Retrieve all stored Notion API tokens with masked values."
)
async def list_tokens(
    token_service: Annotated[TokenService, Depends(get_token_service)],
    active_only: bool = Query(True, description="Filter to only active tokens")
) -> TokenListResponse:
    """
    List all Notion API tokens.
    
    - **active_only**: If true, only return active tokens (default: true)
    
    Returns list of tokens with masked values.
    """
    return await token_service.list_tokens(active_only=active_only)


@router.get(
    "/{token_id}",
    response_model=TokenResponse,
    summary="Get a Notion API token by ID",
    description="Retrieve a single Notion API token with masked value."
)
async def get_token(
    token_id: str,
    token_service: Annotated[TokenService, Depends(get_token_service)]
) -> TokenResponse:
    """
    Get a single Notion API token by ID.
    
    - **token_id**: Token ID to retrieve
    
    Returns the token with masked value.
    """
    return await token_service.get_token(token_id)


@router.patch(
    "/{token_id}",
    response_model=TokenResponse,
    summary="Update a Notion API token",
    description="Update name, description, or active status of a token."
)
async def update_token(
    token_id: str,
    request: UpdateTokenRequest,
    token_service: Annotated[TokenService, Depends(get_token_service)]
) -> TokenResponse:
    """
    Update a Notion API token.
    
    - **token_id**: Token ID to update
    - **name**: Optional new name
    - **description**: Optional new description
    - **is_active**: Optional active status
    
    Returns the updated token with masked value.
    """
    return await token_service.update_token(token_id, request)


@router.delete(
    "/{token_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a Notion API token",
    description="Permanently delete a Notion API token."
)
async def delete_token(
    token_id: str,
    token_service: Annotated[TokenService, Depends(get_token_service)]
) -> Response:
    """
    Delete a Notion API token.
    
    - **token_id**: Token ID to delete
    
    Returns 204 No Content on success.
    """
    await token_service.delete_token(token_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
