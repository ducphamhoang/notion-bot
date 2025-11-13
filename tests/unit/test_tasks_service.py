"""Unit tests for Notion task service."""

import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from notion_client import APIResponseError
from notion_client.errors import HTTPResponseError

from src.features.tasks.dto.create_task_request import CreateTaskRequest
from src.features.tasks.dto.create_task_response import CreateTaskResponse
from src.features.tasks.services.notion_task_service import NotionTaskService
from src.core.errors.exceptions import NotionAPIError, NotFoundError, ValidationError


class MockAPIResponseError(APIResponseError):
    """Mock APIResponseError for testing."""
    def __init__(self, status: int, message: str, code: str, **kwargs):
        # Set attributes without calling parent __init__ since it has complex requirements
        self.status = status
        self.body = {"message": message, **kwargs}
        self.code = code
        # Call Exception.__init__ directly to avoid APIResponseError's complex constructor
        Exception.__init__(self, f"{code}: {message}")


def create_mock_api_error(status: int, message: str, code: str, **kwargs):
    """Create a mock APIResponseError with required attributes."""
    return MockAPIResponseError(status, message, code, **kwargs)


class TestNotionTaskService:
    """Test cases for NotionTaskService."""
    
    @pytest.fixture
    def task_service(self):
        """Create test task service instance."""
        return NotionTaskService()
    
    @pytest.fixture
    def sample_request(self):
        """Sample create task request."""
        return CreateTaskRequest(
            title="Test Task",
            notion_database_id="1a2b3c4d5e6f7890abcdef1234567890",
            assignee_id="user_001",
            due_date=datetime(2023, 7, 25),
            priority="High",
            properties={
                "Tags": {"multi_select": [{"name": "bug"}]}
            }
        )
    
    @pytest.mark.asyncio
    async def test_build_notion_properties_basic(self, task_service, sample_request):
        """Test building basic Notion properties."""
        properties = task_service._build_notion_properties(sample_request)

        assert "Name" in properties
        assert properties["Name"]["title"][0]["text"]["content"] == "Test Task"
        assert "Due Date" in properties
        assert properties["Due Date"]["date"]["start"] == "2023-07-25T00:00:00"
        assert "Priority" in properties
        assert properties["Priority"]["select"]["name"] == "High"

    @pytest.mark.asyncio
    async def test_build_notion_properties_custom_mappings(self, task_service, sample_request):
        """Test building properties with custom mappings."""
        custom_mappings = {
            "title": "Task Name",
            "due_date": "Deadline",
            "priority": "Importance",
            "assignee": "Owner",
            "status": "State"
        }

        properties = task_service._build_notion_properties(sample_request, custom_mappings)

        # Check custom property names are used
        assert "Task Name" in properties
        assert "Deadline" in properties
        assert "Importance" in properties
        assert properties["Task Name"]["title"][0]["text"]["content"] == "Test Task"
    
    @pytest.mark.asyncio
    async def test_build_notion_properties_custom_merge(self, task_service, sample_request):
        """Test merging custom properties."""
        sample_request.properties = {
            "Custom Field": {"rich_text": [{"text": {"content": "Custom"}}]},
            "Priority": {"select": {"name": "Low"}}  # Override base property
        }
        
        properties = task_service._build_notion_properties(sample_request)
        
        # Ensure custom field is added
        assert "Custom Field" in properties
        assert properties["Custom Field"]["rich_text"][0]["text"]["content"] == "Custom"
        
        # Ensure custom property overrides base property
        assert properties["Priority"]["select"]["name"] == "Low"
    
    @pytest.mark.asyncio
    async def test_create_task_success(self, sample_request):
        """Test successful task creation."""
        # Mock Notion client response
        mock_response = {
            "id": "returned-task-id",
            "url": "https://notion.so/returned-task-id",
            "created_time": datetime.utcnow().isoformat()
        }

        # Create mock client
        mock_client = AsyncMock()
        mock_client.pages.create = AsyncMock(return_value=mock_response)

        # Inject mock client via DI
        task_service = NotionTaskService(notion_client=mock_client)

        result = await task_service.create_task(sample_request)

        # Verify response
        assert isinstance(result, CreateTaskResponse)
        assert result.notion_task_id == "returned-task-id"
        assert result.notion_task_url == "https://notion.so/returned-task-id"
        assert isinstance(result.created_at, datetime)

        # Verify client was called correctly
        mock_client.pages.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_task_database_not_found(self, sample_request):
        """Test task creation with invalid database ID."""
        # Create mock client that raises 404
        mock_client = AsyncMock()
        mock_client.pages.create.side_effect = create_mock_api_error(
            status=404,
            message="Database not found",
            code="object_not_found"
        )

        # Inject mock client
        task_service = NotionTaskService(notion_client=mock_client)

        with pytest.raises(NotFoundError) as exc_info:
            await task_service.create_task(sample_request)

        assert exc_info.value.entity_type == "database"
        assert exc_info.value.entity_id == sample_request.notion_database_id
    
    @pytest.mark.asyncio
    async def test_create_task_validation_error(self, sample_request):
        """Test task creation with validation error."""
        mock_client = AsyncMock()
        mock_client.pages.create.side_effect = create_mock_api_error(
            status=400,
            message="Invalid property",
            code="validation_error",
            field="title"
        )

        task_service = NotionTaskService(notion_client=mock_client)

        with pytest.raises(ValidationError) as exc_info:
            await task_service.create_task(sample_request)

        assert "Invalid task data" in str(exc_info.value)
        assert exc_info.value.field == "title"
    
    @pytest.mark.asyncio
    async def test_create_task_notion_api_error(self, sample_request):
        """Test task creation with generic Notion API error."""
        mock_client = AsyncMock()
        mock_client.pages.create.side_effect = create_mock_api_error(
            status=500,
            message="Internal server error",
            code="internal_server_error"
        )

        task_service = NotionTaskService(notion_client=mock_client)

        with pytest.raises(NotionAPIError) as exc_info:
            await task_service.create_task(sample_request)

        assert "Failed to create task" in str(exc_info.value)
        assert exc_info.value.status_code == 500
    
    @pytest.mark.asyncio
    async def test_test_database_access_success(self):
        """Test successful database access check."""
        database_id = "1a2b3c4d5e6f7890abcdef1234567890"

        mock_database = {
            "title": [{"text": {"content": "Test Database"}}],
            "properties": {"Name": {"title": {}}}
        }

        with patch('src.features.tasks.services.notion_task_service.get_notion_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.databases.retrieve = AsyncMock(return_value=mock_database)
            mock_get_client.return_value = mock_client

            task_service = NotionTaskService()
            result = await task_service.test_database_access(database_id)

            assert result["accessible"] is True
            assert result["database_id"] == database_id
            assert result["database_name"] == "Test Database"
            assert "properties" in result
    
    @pytest.mark.asyncio
    async def test_test_database_access_not_found(self):
        """Test database access check with invalid database."""
        database_id = "invalid_database_id"

        with patch('src.features.tasks.services.notion_task_service.get_notion_client') as mock_get_client:
            mock_client = AsyncMock()
            mock_client.databases.retrieve.side_effect = create_mock_api_error(
                status=404,
                message="Database not found",
                code="object_not_found"
            )
            mock_get_client.return_value = mock_client

            task_service = NotionTaskService()

            with pytest.raises(NotFoundError) as exc_info:
                await task_service.test_database_access(database_id)

            assert exc_info.value.entity_type == "database"
            assert exc_info.value.entity_id == database_id
