"""Service layer for Notion task operations."""

import logging
from datetime import datetime

from notion_client import AsyncClient, APIResponseError

from src.config.settings import get_settings
from src.core.notion.client import get_notion_client
from src.core.notion.rate_limiter import with_retry
from src.core.errors.exceptions import (
    NotionAPIError,
    NotFoundError,
    ValidationError,
    InternalError
)
from src.features.tasks.dto.create_task_request import CreateTaskRequest
from src.features.tasks.dto.create_task_response import CreateTaskResponse

logger = logging.getLogger(__name__)


class NotionTaskService:
    """Service for managing tasks in Notion databases."""

    def __init__(self, notion_client: AsyncClient | None = None):
        """
        Initialize NotionTaskService.

        Args:
            notion_client: Notion client instance (injected for DI)
        """
        self._notion_client = notion_client

    async def _get_client(self) -> AsyncClient:
        """Get Notion client instance, creating if not injected."""
        if self._notion_client is None:
            self._notion_client = await get_notion_client()
        return self._notion_client
    
    @with_retry(
        max_retries=4,
        initial_delay=1.0,
        max_delay=8.0,
        jitter_factor=0.2
    )
    async def create_task(self, request: CreateTaskRequest) -> CreateTaskResponse:
        """
        Create a new task in Notion database.
        
        Args:
            request: Task creation request with all required fields
            
        Returns:
            CreateTaskResponse with task details
            
        Raises:
            ValidationError: If request validation fails
            NotFoundError: If Notion database is not found
            NotionAPIError: If Notion API call fails
            InternalError: For unexpected errors
        """
        try:
            # Get client
            client = await self._get_client()

            # TODO: Resolve assignee_id via user mapping service (Feature 6)
            # When user mapping service is implemented:
            # if request.assignee_id:
            #     from features.users.services.user_mapping_service import UserMappingService
            #     user_service = UserMappingService()
            #     notion_assignee_id = await user_service.resolve_notion_user_id(
            #         platform="web",
            #         platform_user_id=request.assignee_id
            #     )

            # Build Notion properties
            properties = self._build_notion_properties(request)

            # Create the page in Notion
            notion_page = await client.pages.create(
                parent={"database_id": request.notion_database_id},
                properties=properties
            )
            
            # Return response
            return CreateTaskResponse(
                notion_task_id=notion_page["id"],
                notion_task_url=notion_page["url"],
                created_at=datetime.fromisoformat(notion_page["created_time"])
            )
            
        except APIResponseError as e:
            # Map Notion API errors to domain errors
            if e.status == 404:
                raise NotFoundError("database", request.notion_database_id)
            elif e.status == 400:
                raise ValidationError(
                    f"Invalid task data: {e.body.get('message', 'Bad request')}",
                    field=e.body.get('field')
                )
            else:
                raise NotionAPIError(
                    f"Failed to create task: {str(e)}",
                    api_error=e.body,
                    status_code=e.status
                )
        
        except Exception as e:
            logger.error(f"Unexpected error creating task: {str(e)}")
            raise InternalError("Failed to create task", original_error=e)
    
    def _build_notion_properties(
        self,
        request: CreateTaskRequest,
        property_mappings: dict | None = None
    ) -> dict:
        """
        Build Notion page properties from request.

        Args:
            request: Task creation request
            property_mappings: Optional custom property name mappings

        Returns:
            Dictionary of Notion properties
        """
        # Default property mappings (can be overridden via workspace config)
        if property_mappings is None:
            property_mappings = {
                "title": "Name",
                "due_date": "Due Date",
                "priority": "Priority",
                "assignee": "Assignee",
                "status": "Status"
            }

        # Base properties
        properties = {
            property_mappings["title"]: {
                "title": [
                    {"text": {"content": request.title}}
                ]
            }
        }

        # Add optional properties if provided
        if request.due_date:
            properties[property_mappings["due_date"]] = {
                "date": {
                    "start": request.due_date.isoformat()
                }
            }

        if request.priority:
            properties[property_mappings["priority"]] = {
                "select": {
                    "name": request.priority
                }
            }

        # TODO: Add assignee handling when user mapping service is implemented
        # if request.assignee_id and notion_assignee_id:
        #     properties[property_mappings["assignee"]] = {
        #         "people": [{"id": notion_assignee_id}]
        #     }

        # Merge custom properties (takes precedence)
        if request.properties:
            properties.update(request.properties)

        return properties
    
    async def test_database_access(self, database_id: str) -> dict:
        """
        Test if we can access a Notion database.
        
        Args:
            database_id: Notion database ID to test
            
        Returns:
            Dictionary with test results
            
        Raises:
            NotFoundError: If database not found
            NotionAPIError: If API call fails
        """
        try:
            client = await get_notion_client()
            
            # Try to retrieve database info
            database = await client.databases.retrieve(database_id)
            
            return {
                "accessible": True,
                "database_id": database_id,
                "database_name": database.get("title", [{"text": {"content": "Untitled"}}])[0]["text"]["content"],
                "properties": database.get("properties", {})
            }
            
        except APIResponseError as e:
            if e.status == 404:
                raise NotFoundError("database", database_id)
            else:
                raise NotionAPIError(
                    f"Failed to access database: {str(e)}",
                    status_code=e.status
                )
        
        except Exception as e:
            raise InternalError("Failed to test database access", original_error=e)
