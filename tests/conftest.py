"""Test configuration for pytest."""

import pytest
import pytest_asyncio
from typing import AsyncGenerator
import asyncio
import httpx
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from datetime import datetime

from src.main import app
from src.core.database.connection import DatabaseConnection
from src.config.settings import Settings


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_database_connection():
    """Automatically mock database connection for all tests."""
    with patch.object(DatabaseConnection, 'get_database') as mock_get_db, \
         patch.object(DatabaseConnection, 'health_check', new_callable=AsyncMock) as mock_health_check:
        mock_db_instance = AsyncMock()
        mock_get_db.return_value = mock_db_instance
        # Mock health check to return healthy status
        mock_health_check.return_value = {
            "status": "healthy",
            "message": "Database connection is healthy"
        }
        yield mock_db_instance


@pytest.fixture(autouse=True)
def mock_notion_client():
    """Automatically mock Notion API client for all tests."""
    with patch('src.core.notion.client.get_notion_client', new_callable=AsyncMock) as mock_get_client, \
         patch('src.core.notion.client.test_notion_connection', new_callable=AsyncMock) as mock_test_conn:
        
        # Mock the Notion client instance
        mock_client = AsyncMock()
        mock_client.databases.list = AsyncMock(return_value={"results": []})
        mock_client.databases.query = AsyncMock(return_value={"results": [], "has_more": False})
        mock_client.pages.create = AsyncMock(return_value={
            "id": "test-page-id-123",
            "url": "https://notion.so/test-page"
        })
        mock_client.pages.retrieve = AsyncMock(return_value={
            "id": "test-page-id-123",
            "properties": {}
        })
        mock_client.pages.update = AsyncMock(return_value={
            "id": "test-page-id-123"
        })
        mock_get_client.return_value = mock_client
        
        # Mock the health check function
        mock_test_conn.return_value = {
            "status": "healthy",
            "notion_api": {
                "status": "connected",
                "api_version": "connected"
            }
        }
        
        yield mock_client


@pytest.fixture(autouse=True)
def mock_health_cache():
    """Automatically mock health check cache for all tests."""
    with patch('src.core.monitoring.metrics.get_health_cache') as mock_get_cache:
        mock_cache = AsyncMock()
        mock_cache.get.return_value = None  # Return None so cache logic calls the actual checks
        mock_get_cache.return_value = mock_cache
        yield mock_cache


@pytest.fixture(autouse=True)
def mock_task_service():
    """Mock the NotionTaskService for integration tests."""
    with patch('src.features.tasks.services.notion_task_service.get_notion_client', new_callable=AsyncMock) as mock_get_client:
        mock_client = AsyncMock()
        
        # Mock database query (for list_tasks)
        mock_client.databases.query = AsyncMock(return_value={
            "results": [
                {
                    "id": "test-task-1",
                    "properties": {
                        "Name": {"title": [{"plain_text": "Test Task 1"}]},
                        "Status": {"status": {"name": "In Progress"}}
                    },
                    "url": "https://notion.so/test-task-1"
                }
            ],
            "has_more": False,
            "next_cursor": None
        })
        
        # Mock page creation (for create_task)
        mock_client.pages.create = AsyncMock(return_value={
            "id": "1a2b3c4d5e6f7890abcdef1234567890",
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
            "properties": {
                "Name": {"title": [{"plain_text": "Test Task"}]},
                "Status": {"status": {"name": "To Do"}}
            },
            "url": "https://notion.so/test-task"
        })
        
        # Mock page update (for update_task)
        mock_client.pages.update = AsyncMock(return_value={
            "id": "1a2b3c4d5e6f7890abcdef1234567890",
            "created_time": "2024-01-01T00:00:00.000Z",
            "last_edited_time": "2024-01-01T00:00:00.000Z",
            "properties": {
                "Name": {"title": [{"plain_text": "Test Task"}]},
                "Status": {"status": {"name": "Done"}}
            },
            "url": "https://notion.so/test-task"
        })
        
        # Mock page retrieval (for get_task)
        mock_client.pages.retrieve = AsyncMock(return_value={
            "id": "1a2b3c4d5e6f7890abcdef1234567890",
            "properties": {
                "Name": {"title": [{"plain_text": "Test Task"}]},
                "Status": {"status": {"name": "To Do"}}
            },
            "url": "https://notion.so/test-task"
        })
        
        # Mock page archival (for delete_task)
        mock_client.pages.update = AsyncMock(return_value={
            "id": "1a2b3c4d5e6f7890abcdef1234567890",
            "archived": True
        })
        
        mock_get_client.return_value = mock_client
        yield mock_client


@pytest.fixture(autouse=True)
def mock_workspace_service():
    """Mock workspace repository using dependency injection pattern."""
    from src.features.workspaces.models import Workspace
    from src.features.workspaces.repository import WorkspaceRepository
    from src.features.workspaces.routes import get_workspace_service
    from bson import ObjectId
    
    # Create a proper workspace object to return
    object_id = ObjectId()
    workspace_data = {
        "_id": object_id,
        "platform": "slack",
        "platform_id": "C123456789",
        "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
        "name": "Test Workspace",
        "created_at": datetime(2024, 1, 1, 0, 0, 0),
        "updated_at": datetime(2024, 1, 1, 0, 0, 0)
    }
    workspace_obj = Workspace(**workspace_data)
    
    # Create mock repository with proper spec
    mock_repo = AsyncMock(spec=WorkspaceRepository)
    
    # Mock create to return the workspace that was just created
    async def mock_create(workspace_data):
        # Return a new workspace object with the created data
        new_workspace = Workspace(
            _id=ObjectId(),
            platform=workspace_data.platform,
            platform_id=workspace_data.platform_id,
            notion_database_id=workspace_data.notion_database_id,
            name=workspace_data.name,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        # Store it for later retrieval
        mock_repo._workspaces = getattr(mock_repo, '_workspaces', {})
        mock_repo._workspaces[(workspace_data.platform, workspace_data.platform_id)] = new_workspace
        return new_workspace
    
    # Mock find_by_platform_id to return workspace if it exists
    async def mock_find_by_platform_id(platform, platform_id):
        workspaces = getattr(mock_repo, '_workspaces', {})
        return workspaces.get((platform, platform_id))
    
    mock_repo.create = mock_create
    mock_repo.find_by_platform_id = mock_find_by_platform_id
    mock_repo.list_all = AsyncMock(return_value=[workspace_obj])
    mock_repo.find_by_id = AsyncMock(return_value=workspace_obj)
    
    # Mock Notion client for validation
    with patch('src.features.workspaces.services.workspace_service.get_notion_client', new_callable=AsyncMock) as mock_get_client:
        mock_client = AsyncMock()
        mock_client.databases.retrieve = AsyncMock(return_value={"id": "1a2b3c4d5e6f7890abcdef1234567890"})
        mock_client.databases.query = AsyncMock(return_value={"results": []})
        mock_get_client.return_value = mock_client
        
        # Override the dependency to inject our mock repository
        async def override_get_workspace_service():
            from src.features.workspaces.services.workspace_service import WorkspaceService
            return WorkspaceService(repository=mock_repo)
        
        from src.main import app
        app.dependency_overrides[get_workspace_service] = override_get_workspace_service
        
        yield mock_repo
        
        # Cleanup: remove override
        app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_user_repository():
    """Mock user repository using dependency injection pattern."""
    from src.features.users.models import UserMappingInDB
    from src.features.users.repository import UserMappingRepository
    from src.features.users.routes import get_user_mapping_service
    from bson import ObjectId
    
    # Create proper user mapping object
    object_id_str = str(ObjectId())
    user_data = {
        "_id": object_id_str,
        "platform": "teams",
        "platform_user_id": "user-123",
        "notion_user_id": "notion-user-123",
        "created_at": datetime(2024, 1, 1, 0, 0, 0),
        "updated_at": datetime(2024, 1, 1, 0, 0, 0)
    }
    user_obj = UserMappingInDB(**user_data)
    
    # Create mock repository with proper spec
    mock_repo = AsyncMock(spec=UserMappingRepository)
    
    # Mock create_mapping to store and return the created mapping
    async def mock_create_mapping(mapping):
        new_mapping = UserMappingInDB(
            _id=str(ObjectId()),
            platform=mapping.platform,
            platform_user_id=mapping.platform_user_id,
            notion_user_id=mapping.notion_user_id,
            display_name=mapping.display_name,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        # Store for later retrieval
        mock_repo._mappings = getattr(mock_repo, '_mappings', {})
        mock_repo._mappings[(mapping.platform, mapping.platform_user_id)] = new_mapping
        mock_repo._mappings_by_id = getattr(mock_repo, '_mappings_by_id', {})
        mock_repo._mappings_by_id[str(new_mapping.id)] = new_mapping
        return new_mapping
    
    # Mock find methods
    async def mock_find_by_id(mapping_id):
        mappings = getattr(mock_repo, '_mappings_by_id', {})
        return mappings.get(mapping_id)
    
    async def mock_find_by_platform_and_user_id(platform, platform_user_id):
        mappings = getattr(mock_repo, '_mappings', {})
        return mappings.get((platform, platform_user_id))
    
    async def mock_list_mappings(platform, platform_user_id, skip, limit):
        mappings = getattr(mock_repo, '_mappings', {})
        all_mappings = list(mappings.values())
        return (all_mappings[skip:skip+limit], len(all_mappings))
    
    mock_repo.create_mapping = mock_create_mapping
    mock_repo.find_by_id = mock_find_by_id
    mock_repo.find_by_platform_and_user_id = mock_find_by_platform_and_user_id
    mock_repo.list_mappings = mock_list_mappings
    
    # Override the dependency to inject our mock repository
    async def override_get_user_mapping_service():
        from src.features.users.services.user_mapping_service import UserMappingService
        return UserMappingService(repository=mock_repo)
    
    from src.main import app
    app.dependency_overrides[get_user_mapping_service] = override_get_user_mapping_service
    
    yield mock_repo
    
    # Cleanup: remove override
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """Test client for API testing with mocked dependencies."""
    # Use httpx's ASGI transport to test the FastAPI app directly
    # Follow redirects to handle trailing slash issues
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), 
        base_url="http://test",
        follow_redirects=True
    ) as ac:
        yield ac


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch('src.config.settings.get_settings') as mock:
        mock.return_value = Settings(
            mongodb_uri="mongodb://localhost:27017/test_notion_bot",
            notion_api_key="test_key",
            notion_api_version="2022-06-28",
            api_host="0.0.0.0",
            api_port=8000,
            debug=True,
            cors_origins="http://localhost:3000,http://localhost:8000",
            log_level="INFO"
        )
        yield mock