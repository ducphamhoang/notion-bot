"""Service for workspace operations."""

from typing import Optional
from src.features.workspaces.repository import WorkspaceRepository
from src.features.workspaces.dto.create_workspace_request import CreateWorkspaceRequest
from src.features.workspaces.dto.workspace_response import WorkspaceResponse, WorkspaceListResponse
from src.features.workspaces.models import WorkspaceCreate, Workspace
from src.core.errors.exceptions import NotFoundError, ConflictError
from src.core.notion.client import get_notion_client


class WorkspaceService:
    """Service for managing workspace mappings between platforms and Notion databases."""

    def __init__(self, repository: WorkspaceRepository):
        """Initialize the service with a repository."""
        self._repository = repository

    async def create_workspace(self, request: CreateWorkspaceRequest) -> WorkspaceResponse:
        """Create a new workspace mapping."""
        # Convert DTO to model for repository
        workspace_create = WorkspaceCreate(
            platform=request.platform,
            platform_id=request.platform_id,
            notion_database_id=request.notion_database_id,
            name=request.name
        )

        # Validate that the Notion database exists by querying it
        await self._validate_notion_database(workspace_create.notion_database_id)

        # Create the workspace using the repository
        workspace = await self._repository.create(workspace_create)

        # Convert to response DTO
        return WorkspaceResponse.from_workspace(workspace)

    async def get_workspace_by_platform(self, platform: str, platform_id: str) -> WorkspaceResponse:
        """Get a workspace by platform and platform ID."""
        workspace = await self._repository.find_by_platform_id(platform, platform_id)

        if not workspace:
            raise NotFoundError(
                entity_type="Workspace",
                entity_id=f"{platform}:{platform_id}",
                details={
                    "platform": platform,
                    "platform_id": platform_id,
                    "message": f"No workspace mapping found for platform '{platform}' and platform_id '{platform_id}'"
                }
            )

        return WorkspaceResponse.from_workspace(workspace)

    async def list_workspaces(self, platform: Optional[str] = None) -> WorkspaceListResponse:
        """List all workspaces, optionally filtered by platform."""
        workspaces = await self._repository.list_all(platform)

        workspace_responses = [
            WorkspaceResponse.from_workspace(workspace)
            for workspace in workspaces
        ]

        return WorkspaceListResponse(
            workspaces=workspace_responses,
            count=len(workspace_responses)
        )

    async def _validate_notion_database(self, notion_database_id: str) -> None:
        """Validate that the Notion database exists by querying it."""
        try:
            client = await get_notion_client()
            # Try to retrieve the database info
            await client.databases.retrieve(database_id=notion_database_id)
        except Exception as e:
            raise NotFoundError(
                entity_type="NotionDatabase",
                entity_id=notion_database_id,
                details={
                    "notion_database_id": notion_database_id,
                    "error": str(e),
                    "message": f"Notion database '{notion_database_id}' not found or inaccessible"
                }
            )