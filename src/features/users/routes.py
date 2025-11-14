"""API routes for user mapping operations."""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from src.core.database.connection import DatabaseConnection
from src.features.users.dto.create_user_mapping_request import CreateUserMappingRequest
from src.features.users.dto.user_mapping_response import UserMappingResponse
from src.features.users.dto.list_user_mappings_response import ListUserMappingsResponse
from src.features.users.repository import UserMappingRepository
from src.features.users.services.user_mapping_service import UserMappingService


# Create router
router = APIRouter(prefix="/users/mappings", tags=["user-mappings"])


def get_user_mapping_service() -> UserMappingService:
    """Dependency to get user mapping service instance."""
    db_connection = DatabaseConnection()
    repository = UserMappingRepository(db_connection)
    return UserMappingService(repository)


@router.post("/", response_model=UserMappingResponse, status_code=201)
async def create_user_mapping(
    request: CreateUserMappingRequest,
    service: Annotated[UserMappingService, Depends(get_user_mapping_service)]
) -> UserMappingResponse:
    """
    Create a new user mapping between a platform user and a Notion user.
    
    This allows mapping platform users (e.g., Slack, Teams) to their corresponding Notion users 
    for proper assignee resolution when creating or updating tasks.
    """
    return await service.create_mapping(request)


@router.get("/", response_model=ListUserMappingsResponse)
async def list_user_mappings(
    service: Annotated[UserMappingService, Depends(get_user_mapping_service)],
    platform: Optional[str] = Query(None, description="Filter by platform (e.g., 'slack', 'teams')"),
    platform_user_id: Optional[str] = Query(None, description="Filter by platform user ID"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page")
) -> ListUserMappingsResponse:
    """
    List user mappings with optional filtering.

    Query parameters:
    - platform: Filter by platform (e.g., 'slack', 'teams')
    - platform_user_id: Filter by platform user ID
    - page: Page number for pagination (default: 1)
    - limit: Number of items per page (default: 20, max: 100)
    """
    return await service.list_mappings(platform, platform_user_id, page, limit)


@router.get("/{mapping_id}", response_model=UserMappingResponse)
async def get_user_mapping_by_id(
    mapping_id: str,
    service: Annotated[UserMappingService, Depends(get_user_mapping_service)]
) -> UserMappingResponse:
    """
    Get a user mapping by its database ID.
    """
    return await service.get_mapping_by_id(mapping_id)


@router.get("/resolve", response_model=UserMappingResponse)
async def resolve_user_mapping(
    platform: str,
    platform_user_id: str,
    service: Annotated[UserMappingService, Depends(get_user_mapping_service)]
) -> UserMappingResponse:
    """
    Resolve a user mapping by platform and platform user ID.

    Query parameters:
    - platform: Platform identifier (e.g., 'slack', 'teams')
    - platform_user_id: User ID in the platform
    """
    # Get the full mapping details
    return await service.get_mapping_by_platform_and_user_id(platform, platform_user_id)