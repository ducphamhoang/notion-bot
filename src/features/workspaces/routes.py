"""API routes for workspace management."""

import logging
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse

# Exception handlers are handled globally in main.py
from src.core.database.connection import DatabaseConnection
from src.features.workspaces.dto.create_workspace_request import CreateWorkspaceRequest
from src.features.workspaces.dto.workspace_response import WorkspaceResponse, WorkspaceListResponse
from src.features.workspaces.repository import WorkspaceRepository
from src.features.workspaces.services.workspace_service import WorkspaceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


async def get_workspace_service() -> WorkspaceService:
    """Dependency injection for workspace service."""
    db_connection = DatabaseConnection()
    repository = WorkspaceRepository(await db_connection.get_database())
    return WorkspaceService(repository=repository)


@router.post(
    "/",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a workspace mapping",
    description="Create a new mapping between a platform workspace and a Notion database."
)
async def create_workspace(
    request: CreateWorkspaceRequest,
    workspace_service: WorkspaceService = Depends(get_workspace_service)
) -> WorkspaceResponse:
    """
    Create a new workspace mapping.
    
    - **platform**: Platform name: teams|slack|web
    - **platform_id**: Channel or workspace ID on platform
    - **notion_database_id**: Target Notion database UUID
    - **name**: Human-readable workspace name
    
    Returns the created workspace mapping details.
    """
    return await workspace_service.create_workspace(request)


@router.get(
    "/query",
    response_model=WorkspaceResponse,
    summary="Get workspace by platform",
    description="Retrieve workspace mapping by platform and platform ID."
)
async def get_workspace_by_platform(
    platform: str = Query(..., description="Platform name: teams|slack|web"),
    platform_id: str = Query(..., description="Platform workspace/channel ID"),
    workspace_service: WorkspaceService = Depends(get_workspace_service)
) -> WorkspaceResponse:
    """
    Get workspace mapping by platform and platform ID.
    
    Query parameters:
    - **platform**: Platform name
    - **platform_id**: Platform workspace/channel ID
    
    Returns workspace mapping details.
    """
    return await workspace_service.get_workspace_by_platform(platform, platform_id)


@router.get(
    "/",
    response_model=WorkspaceListResponse,
    summary="List workspace mappings",
    description="List all workspace mappings, optionally filtered by platform."
)
async def list_workspaces(
    platform: Optional[str] = Query(
        None, 
        description="Filter by platform name: teams|slack|web"
    ),
    workspace_service: WorkspaceService = Depends(get_workspace_service)
) -> WorkspaceListResponse:
    """
    List all workspace mappings.
    
    Query parameters:
    - **platform**: Optional filter by platform name
    
    Returns list of workspace mappings with count.
    """
    return await workspace_service.list_workspaces(platform)


# Exception handlers are handled globally in main.py
