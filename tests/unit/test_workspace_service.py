"""Unit tests for workspace service."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.features.workspaces.dto.create_workspace_request import CreateWorkspaceRequest
from src.features.workspaces.services.workspace_service import WorkspaceService
from src.features.workspaces.models import Workspace
from src.core.errors.exceptions import NotFoundError
from bson import ObjectId


@pytest.fixture
def mock_repository():
    """Mock repository for testing."""
    return AsyncMock()


@pytest.fixture
def workspace_service(mock_repository):
    """Create workspace service instance with mock repository."""
    return WorkspaceService(repository=mock_repository)


@pytest.mark.asyncio
async def test_create_workspace_success(workspace_service, mock_repository):
    """Test successful creation of workspace."""
    # Arrange
    request = CreateWorkspaceRequest(
        platform="slack",
        platform_id="C123456",
        notion_database_id="12345678123456781234567812345678",
        name="Test Workspace"
    )
    
    workspace_data = MagicMock()
    workspace_data.id = ObjectId()
    workspace_data.platform = request.platform
    workspace_data.platform_id = request.platform_id
    workspace_data.notion_database_id = request.notion_database_id
    workspace_data.name = request.name
    
    mock_repository.create.return_value = workspace_data
    
    # Mock the validate_notion_database method
    workspace_service._validate_notion_database = AsyncMock(return_value=None)
    
    # Act
    result = await workspace_service.create_workspace(request)
    
    # Assert
    assert result.platform == request.platform
    assert result.platform_id == request.platform_id
    assert result.notion_database_id == request.notion_database_id
    assert result.name == request.name
    mock_repository.create.assert_called_once()
    workspace_service._validate_notion_database.assert_called_once_with(request.notion_database_id)


@pytest.mark.asyncio
async def test_get_workspace_by_platform_success(workspace_service, mock_repository):
    """Test successful retrieval of workspace by platform and platform ID."""
    # Arrange
    platform = "slack"
    platform_id = "C123456"
    
    workspace_data = MagicMock()
    workspace_data.id = ObjectId()
    workspace_data.platform = platform
    workspace_data.platform_id = platform_id
    workspace_data.notion_database_id = "12345678123456781234567812345678"
    workspace_data.name = "Test Workspace"
    
    mock_repository.find_by_platform_id.return_value = workspace_data
    
    # Act
    result = await workspace_service.get_workspace_by_platform(platform, platform_id)
    
    # Assert
    assert result.platform == platform
    assert result.platform_id == platform_id
    mock_repository.find_by_platform_id.assert_called_once_with(platform, platform_id)


@pytest.mark.asyncio
async def test_get_workspace_by_platform_not_found(workspace_service, mock_repository):
    """Test retrieval failure when workspace doesn't exist."""
    # Arrange
    platform = "slack"
    platform_id = "C123456"
    
    mock_repository.find_by_platform_id.return_value = None
    
    # Act & Assert
    with pytest.raises(NotFoundError) as exc_info:
        await workspace_service.get_workspace_by_platform(platform, platform_id)
    
    assert exc_info.value.entity_type == "Workspace"
    assert exc_info.value.entity_id == f"{platform}:{platform_id}"


@pytest.mark.asyncio
async def test_list_workspaces_success(workspace_service, mock_repository):
    """Test successful listing of workspaces."""
    # Arrange
    workspace1 = MagicMock()
    workspace1.id = ObjectId()
    workspace1.platform = "slack"
    workspace1.platform_id = "C123456"
    workspace1.notion_database_id = "12345678123456781234567812345678"
    workspace1.name = "Test Workspace 1"
    
    workspace2 = MagicMock()
    workspace2.id = ObjectId()
    workspace2.platform = "teams"
    workspace2.platform_id = "T789012"
    workspace2.notion_database_id = "87654321876543218765432187654321"
    workspace2.name = "Test Workspace 2"
    
    mock_repository.list_all.return_value = [workspace1, workspace2]
    
    # Act
    result = await workspace_service.list_workspaces()
    
    # Assert
    assert len(result.workspaces) == 2
    assert result.count == 2
    assert result.workspaces[0].platform == "slack"
    assert result.workspaces[1].platform == "teams"
    mock_repository.list_all.assert_called_once_with(None)


@pytest.mark.asyncio
async def test_list_workspaces_with_platform_filter(workspace_service, mock_repository):
    """Test successful listing of workspaces with platform filter."""
    # Arrange
    platform = "slack"
    
    workspace1 = MagicMock()
    workspace1.id = ObjectId()
    workspace1.platform = platform
    workspace1.platform_id = "C123456"
    workspace1.notion_database_id = "12345678123456781234567812345678"
    workspace1.name = "Test Workspace 1"
    
    mock_repository.list_all.return_value = [workspace1]
    
    # Act
    result = await workspace_service.list_workspaces(platform=platform)
    
    # Assert
    assert len(result.workspaces) == 1
    assert result.count == 1
    assert result.workspaces[0].platform == platform
    mock_repository.list_all.assert_called_once_with(platform)