"""Service layer for workspace management operations."""

import logging

from src.core.database.connection import DatabaseConnection
from src.core.errors.exceptions import (
    NotFoundError,
    ConflictError,
    NotionAPIError,
    ValidationError,
    InternalError
)
from src.features.workspaces.repository import WorkspaceRepository
from src.features.workspaces.dto.create_workspace_request import CreateWorkspaceRequest
from src.features.workspaces.dto.workspace_response import WorkspaceResponse, WorkspaceListResponse
from src.features.tasks.services.notion_task_service import NotionTaskService

logger = logging.getLogger(__name__)


class WorkspaceService:
    """Service for managing workspace mappings."""
    
    def __init__(self):
        self.repository = WorkspaceRepository()
        self.notion_service = NotionTaskService()
    
    async def create_workspace(self, request: CreateWorkspaceRequest) -> WorkspaceResponse:
        """
        Create a new workspace mapping.
        
        Args:
            request: Workspace creation request
            
        Returns:
            Created workspace details
            
        Raises:
            ConflictError: If workspace already exists
            ValidationError: If Notion database is invalid
            NotionAPIError: If Notion API call fails
            InternalError: For unexpected errors
        """
        try:
            # Validate Notion database exists and is accessible
            db_check = await self.notion_service.test_database_access(
                request.notion_database_id
            )
            
            # Create workspace in database
            workspace = await self.repository.create(request.to_create_model())
            
            # Convert to response model
            return WorkspaceResponse.from_workspace(workspace)
            
        except ConflictError:
            raise
        except NotFoundError as e:
            raise ValidationError(
                f"Notion database not found: {request.notion_database_id}",
                field="notion_database_id"
            )
        except Exception as e:
            logger.error(f"Error creating workspace: {str(e)}")
            raise InternalError("Failed to create workspace", original_error=e)
    
    async def get_workspace_by_platform(
        self, 
        platform: str, 
        platform_id: str
    ) -> WorkspaceResponse:
        """
        Get workspace by platform and platform_id.
        
        Args:
            platform: Platform name
            platform_id: Platform workspace/channel ID
            
        Returns:
            Workspace details
            
        Raises:
            NotFoundError: If workspace not found
        """
        workspace = await self.repository.find_by_platform_id(platform, platform_id)
        
        if not workspace:
            raise NotFoundError("workspace", f"{platform}/{platform_id}")
        
        return WorkspaceResponse.from_workspace(workspace)
    
    async def list_workspaces(self, platform: str | None = None) -> WorkspaceListResponse:
        """
        List all workspaces, optionally filtered by platform.
        
        Args:
            platform: Optional platform filter
            
        Returns:
            List of workspaces
        """
        try:
            workspaces = await self.repository.list_all(platform)
            
            workspace_responses = [
                WorkspaceResponse.from_workspace(ws) 
                for ws in workspaces
            ]
            
            return WorkspaceListResponse(
                workspaces=workspace_responses,
                count=len(workspace_responses)
            )
            
        except Exception as e:
            logger.error(f"Error listing workspaces: {str(e)}")
            raise InternalError("Failed to list workspaces", original_error=e)
