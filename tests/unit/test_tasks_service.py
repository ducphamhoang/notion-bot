"""Unit tests for Notion task service."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch
from notion_client import APIResponseError

from src.features.tasks.dto.create_task_request import CreateTaskRequest
from src.features.tasks.dto.create_task_response import CreateTaskResponse
from src.features.tasks.dto.list_tasks_request import ListTasksRequest
from src.features.tasks.dto.update_task_request import UpdateTaskRequest
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


def build_notion_page(
    *,
    title: str = "Test Task",
    status: str = "In Progress",
    priority: str = "High",
    due_date: datetime | None = None,
) -> dict:
    """Helper to construct a Notion page payload for testing."""
    due_value = due_date or datetime.utcnow()
    return {
        "id": "task-id-123",
        "url": "https://notion.so/task-id-123",
        "created_time": datetime.utcnow().isoformat() + "Z",
        "last_edited_time": datetime.utcnow().isoformat() + "Z",
        "properties": {
            "Name": {"title": [{"plain_text": title}]},
            "Status": {"status": {"name": status}},
            "Priority": {"select": {"name": priority}},
            "Due Date": {"date": {"start": due_value.isoformat() + "Z"}},
            "Assignee": {"people": [{"name": "Jane Doe", "id": "user_123"}]}
        }
    }


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

    @pytest.mark.asyncio
    async def test_list_tasks_success_returns_summary(self):
        """List tasks returns TaskSummary objects."""
        request = ListTasksRequest(
            notion_database_id="1a2b3c4d5e6f7890abcdef1234567890",
            status="In Progress",
            limit=2
        )

        mock_client = AsyncMock()
        mock_client.databases.query.return_value = {
            "results": [build_notion_page()],
            "has_more": False,
            "next_cursor": None
        }

        service = NotionTaskService(notion_client=mock_client)
        response = await service.list_tasks(request)

        assert response.total == 1
        assert response.data[0].status == "In Progress"
        assert response.data[0].priority == "High"
        mock_client.databases.query.assert_awaited()

    @pytest.mark.asyncio
    async def test_list_tasks_pagination_second_page(self):
        """List tasks fetches additional pages when needed."""
        request = ListTasksRequest(
            notion_database_id="1a2b3c4d5e6f7890abcdef1234567890",
            page=2,
            limit=1
        )

        first_page = build_notion_page(title="First")
        second_page = build_notion_page(title="Second", status="Done")

        mock_client = AsyncMock()
        mock_client.databases.query.side_effect = [
            {
                "results": [first_page],
                "has_more": True,
                "next_cursor": "cursor-1"
            },
            {
                "results": [second_page],
                "has_more": False,
                "next_cursor": None
            }
        ]

        service = NotionTaskService(notion_client=mock_client)
        response = await service.list_tasks(request)

        assert len(response.data) == 1
        assert response.data[0].title == "Second"
        assert response.has_more is False
        assert mock_client.databases.query.await_count == 2

    @pytest.mark.asyncio
    async def test_list_tasks_handles_not_found(self):
        """List tasks propagates Notion 404 as domain error."""
        request = ListTasksRequest(
            notion_database_id="1a2b3c4d5e6f7890abcdef1234567890"
        )

        mock_client = AsyncMock()
        mock_client.databases.query.side_effect = create_mock_api_error(
            status=404,
            message="Database not found",
            code="object_not_found"
        )

        service = NotionTaskService(notion_client=mock_client)

        with pytest.raises(NotFoundError):
            await service.list_tasks(request)

    @pytest.mark.asyncio
    async def test_update_task_success(self):
        """Update task returns response with updated fields."""
        request = UpdateTaskRequest(status="Done")
        mock_client = AsyncMock()
        mock_client.pages.update.return_value = build_notion_page(status="Done")

        service = NotionTaskService(notion_client=mock_client)
        response = await service.update_task("task-id", request)

        assert response.status == "Done"
        assert response.notion_task_id == "task-id-123"
        mock_client.pages.update.assert_awaited()

    @pytest.mark.asyncio
    async def test_update_task_not_found(self):
        """Update task maps Notion 404 to NotFoundError."""
        request = UpdateTaskRequest(status="Done")
        mock_client = AsyncMock()
        mock_client.pages.update.side_effect = create_mock_api_error(
            status=404,
            message="Page not found",
            code="object_not_found"
        )

        service = NotionTaskService(notion_client=mock_client)

        with pytest.raises(NotFoundError):
            await service.update_task("missing", request)

    @pytest.mark.asyncio
    async def test_update_task_validation_error(self):
        """Update task surfaces validation issues from Notion."""
        request = UpdateTaskRequest(status="Done")
        mock_client = AsyncMock()
        mock_client.pages.update.side_effect = create_mock_api_error(
            status=400,
            message="Invalid status",
            code="validation_error"
        )

        service = NotionTaskService(notion_client=mock_client)

        with pytest.raises(ValidationError):
            await service.update_task("task-id", request)

    @pytest.mark.asyncio
    async def test_delete_task_success(self):
        """Delete task archives the page in Notion."""
        mock_client = AsyncMock()
        mock_client.pages.update.return_value = build_notion_page()

        service = NotionTaskService(notion_client=mock_client)
        await service.delete_task("task-id-123")

        mock_client.pages.update.assert_awaited_once_with(
            page_id="task-id-123", archived=True
        )

    @pytest.mark.asyncio
    async def test_delete_task_not_found(self):
        """Delete task maps Notion 404 to NotFoundError."""
        mock_client = AsyncMock()
        mock_client.pages.update.side_effect = create_mock_api_error(
            status=404,
            message="Page not found",
            code="object_not_found"
        )

        service = NotionTaskService(notion_client=mock_client)

        with pytest.raises(NotFoundError):
            await service.delete_task("missing")

    @pytest.mark.asyncio
    async def test_delete_task_validation_error(self):
        """Delete task surfaces validation issues from Notion."""
        mock_client = AsyncMock()
        mock_client.pages.update.side_effect = create_mock_api_error(
            status=400,
            message="Invalid page ID",
            code="validation_error"
        )

        service = NotionTaskService(notion_client=mock_client)

        with pytest.raises(ValidationError):
            await service.delete_task("invalid-id")

    @pytest.mark.asyncio
    async def test_delete_task_notion_api_error(self):
        """Delete task maps other Notion errors to NotionAPIError."""
        mock_client = AsyncMock()
        mock_client.pages.update.side_effect = create_mock_api_error(
            status=500,
            message="Internal server error",
            code="internal_server_error"
        )

        service = NotionTaskService(notion_client=mock_client)

        with pytest.raises(NotionAPIError):
            await service.delete_task("task-id-123")
