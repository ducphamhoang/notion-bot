"""Service for user mapping operations."""

from typing import List, Optional
from src.features.users.dto.create_user_mapping_request import CreateUserMappingRequest
from src.features.users.dto.user_mapping_response import UserMappingResponse
from src.features.users.dto.list_user_mappings_response import ListUserMappingsResponse
from src.features.users.repository import UserMappingRepository
from src.features.users.models import UserMapping
from src.core.errors.exceptions import NotFoundError


class UserMappingService:
    """Service for user mapping operations."""

    def __init__(self, repository: UserMappingRepository):
        """Initialize the service with a repository."""
        self._repository = repository

    async def create_mapping(self, request: CreateUserMappingRequest) -> UserMappingResponse:
        """Create a new user mapping."""
        # Create the UserMapping model from the request
        mapping = UserMapping(
            platform=request.platform,
            platform_user_id=request.platform_user_id,
            notion_user_id=request.notion_user_id,
            display_name=request.display_name
        )

        # Save to database
        created_mapping = await self._repository.create_mapping(mapping)

        # Return response
        return UserMappingResponse(
            id=str(created_mapping.id),
            platform=created_mapping.platform,
            platform_user_id=created_mapping.platform_user_id,
            notion_user_id=created_mapping.notion_user_id,
            display_name=created_mapping.display_name,
            created_at=created_mapping.created_at,
            updated_at=created_mapping.updated_at
        )

    async def resolve_notion_user_id(self, platform: str, platform_user_id: str) -> str:
        """Resolve a platform user ID to its corresponding Notion user ID."""
        mapping = await self._repository.find_by_platform_and_user_id(platform, platform_user_id)

        if not mapping:
            raise NotFoundError(
                entity_type="UserMapping",
                entity_id=f"{platform}:{platform_user_id}",
                details={
                    "platform": platform,
                    "platform_user_id": platform_user_id,
                    "message": f"No user mapping found for platform '{platform}' and platform_user_id '{platform_user_id}'"
                }
            )

        return mapping.notion_user_id

    async def get_mapping_by_platform_and_user_id(self, platform: str, platform_user_id: str) -> UserMappingResponse:
        """Get a user mapping by platform and platform user ID."""
        mapping = await self._repository.find_by_platform_and_user_id(platform, platform_user_id)

        if not mapping:
            raise NotFoundError(
                entity_type="UserMapping",
                entity_id=f"{platform}:{platform_user_id}",
                details={
                    "platform": platform,
                    "platform_user_id": platform_user_id,
                    "message": f"No user mapping found for platform '{platform}' and platform_user_id '{platform_user_id}'"
                }
            )

        return UserMappingResponse(
            id=str(mapping.id),
            platform=mapping.platform,
            platform_user_id=mapping.platform_user_id,
            notion_user_id=mapping.notion_user_id,
            display_name=mapping.display_name,
            created_at=mapping.created_at,
            updated_at=mapping.updated_at
        )

    async def get_mapping_by_id(self, mapping_id: str) -> UserMappingResponse:
        """Get a user mapping by its database ID."""
        mapping = await self._repository.find_by_id(mapping_id)

        if not mapping:
            raise NotFoundError(
                entity_type="UserMapping",
                entity_id=mapping_id,
                details={
                    "mapping_id": mapping_id,
                    "message": f"No user mapping found with ID '{mapping_id}'"
                }
            )

        return UserMappingResponse(
            id=str(mapping.id),
            platform=mapping.platform,
            platform_user_id=mapping.platform_user_id,
            notion_user_id=mapping.notion_user_id,
            display_name=mapping.display_name,
            created_at=mapping.created_at,
            updated_at=mapping.updated_at
        )

    async def list_mappings(
        self,
        platform: Optional[str] = None,
        platform_user_id: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> ListUserMappingsResponse:
        """List user mappings with optional filtering and pagination."""
        skip = (page - 1) * limit
        mappings, total = await self._repository.list_mappings(platform, platform_user_id, skip, limit)

        data = [
            UserMappingResponse(
                id=str(mapping.id),
                platform=mapping.platform,
                platform_user_id=mapping.platform_user_id,
                notion_user_id=mapping.notion_user_id,
                display_name=mapping.display_name,
                created_at=mapping.created_at,
                updated_at=mapping.updated_at
            )
            for mapping in mappings
        ]

        return ListUserMappingsResponse(
            data=data,
            total=total,
            page=page,
            limit=limit,
            has_more=total > page * limit
        )