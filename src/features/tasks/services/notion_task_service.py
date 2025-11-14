"""Service layer for Notion task operations."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from notion_client import APIResponseError, AsyncClient

from src.core.errors.exceptions import (
    InternalError,
    NotFoundError,
    NotionAPIError,
    ValidationError,
)
from src.core.notion.client import get_notion_client
from src.core.notion.rate_limiter import with_retry
from src.features.tasks.dto.create_task_request import CreateTaskRequest
from src.features.tasks.dto.create_task_response import CreateTaskResponse
from src.features.tasks.dto.list_tasks_request import ListTasksRequest
from src.features.tasks.dto.list_tasks_response import ListTasksResponse, TaskSummary
from src.features.tasks.dto.update_task_request import UpdateTaskRequest
from src.features.tasks.dto.update_task_response import UpdateTaskResponse
from src.features.users.services.user_mapping_service import UserMappingService

logger = logging.getLogger(__name__)


class NotionTaskService:
    """Service for managing tasks in Notion databases."""

    DEFAULT_PROPERTY_MAPPINGS: Dict[str, str] = {
        "title": "Name",
        "due_date": "Due Date",
        "priority": "Priority",
        "assignee": "Assignee",
        "status": "Status",
        "project": "Project",
    }

    def __init__(self, notion_client: Optional[AsyncClient] = None, user_mapping_service: Optional[UserMappingService] = None):
        """
        Initialize NotionTaskService.

        Args:
            notion_client: Notion client instance (injected for DI)
            user_mapping_service: User mapping service for resolving assignees (injected for DI)
        """
        self._notion_client = notion_client
        self._user_mapping_service = user_mapping_service

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

            # Resolve assignee_id via user mapping service if provided
            resolved_assignee_id = None
            if request.assignee_id:
                if not self._user_mapping_service:
                    # For backward compatibility and testing, allow assignee_id to be used directly
                    # when user mapping service is not configured
                    # In production, the user mapping service should be configured
                    resolved_assignee_id = request.assignee_id
                else:
                    # For now, we'll assume platform is "web" for direct API usage
                    # In future, we can make this configurable or determine from context
                    resolved_assignee_id = await self._user_mapping_service.resolve_notion_user_id(
                        platform="web",
                        platform_user_id=request.assignee_id
                    )

            # Build Notion properties with resolved assignee ID
            properties = self._build_notion_properties(request, None, resolved_assignee_id)

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
        property_mappings: Optional[Dict[str, str]] = None,
        resolved_assignee_id: Optional[str] = None,
    ) -> dict:
        """
        Build Notion page properties from request.

        Args:
            request: Task creation request
            property_mappings: Optional custom property name mappings
            resolved_assignee_id: Resolved Notion user ID for assignee (if any)

        Returns:
            Dictionary of Notion properties
        """
        resolved_mappings = self._resolve_property_mappings(property_mappings)

        # Base properties
        properties = {
            resolved_mappings["title"]: {
                "title": [
                    {"text": {"content": request.title}}
                ]
            }
        }

        # Add optional properties if provided
        if request.due_date:
            properties[resolved_mappings["due_date"]] = {
                "date": {
                    "start": request.due_date.isoformat()
                }
            }

        if request.priority:
            properties[resolved_mappings["priority"]] = {
                "select": {
                    "name": request.priority
                }
            }

        # Add assignee if resolved
        if resolved_assignee_id:
            properties[resolved_mappings["assignee"]] = {
                "people": [{"id": resolved_assignee_id}]
            }

        # Merge custom properties (takes precedence)
        if request.properties:
            properties.update(request.properties)

        return properties

    def _resolve_property_mappings(
        self,
        overrides: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """Merge default property mappings with any overrides."""
        resolved = self.DEFAULT_PROPERTY_MAPPINGS.copy()
        if overrides:
            resolved.update({k: v for k, v in overrides.items() if isinstance(k, str)})
        return resolved

    @with_retry(
        max_retries=4,
        initial_delay=1.0,
        max_delay=8.0,
        jitter_factor=0.2,
    )
    async def list_tasks(
        self,
        request: ListTasksRequest,
        property_mappings: Optional[Dict[str, str]] = None,
    ) -> ListTasksResponse:
        """Query tasks from Notion with filtering, sorting, and pagination."""
        try:
            client = await self._get_client()
            resolved_mappings = self._resolve_property_mappings(property_mappings)

            notion_filter = self._build_list_filters(request, resolved_mappings)
            sorts = self._build_sort_params(request, resolved_mappings)

            page_size = request.limit
            skip = (request.page - 1) * request.limit
            collected: List[dict[str, Any]] = []
            has_more_for_page = False
            cursor: Optional[str] = None

            while True:
                query_payload: dict[str, Any] = {
                    "database_id": request.notion_database_id,
                    "page_size": min(page_size, 100),
                }
                if notion_filter:
                    query_payload["filter"] = notion_filter
                if sorts:
                    query_payload["sorts"] = sorts
                if cursor:
                    query_payload["start_cursor"] = cursor

                response = await client.databases.query(**query_payload)
                results = response.get("results", [])
                response_has_more = response.get("has_more", False)
                cursor = response.get("next_cursor")

                if skip >= len(results):
                    skip -= len(results)
                else:
                    slice_start = skip
                    slice_end = min(slice_start + (request.limit - len(collected)), len(results))
                    collected.extend(results[slice_start:slice_end])
                    skip = 0
                    remaining_in_batch = len(results) - slice_end
                    if len(collected) >= request.limit:
                        has_more_for_page = remaining_in_batch > 0 or response_has_more
                        break

                if not response_has_more or not cursor:
                    has_more_for_page = False
                    break

            summaries = [
                self._map_page_to_summary(page, resolved_mappings)
                for page in collected
            ]

            return ListTasksResponse(
                data=summaries,
                page=request.page,
                limit=request.limit,
                total=len(summaries),
                has_more=has_more_for_page,
            )

        except APIResponseError as error:
            if error.status == 404:
                raise NotFoundError("database", request.notion_database_id)
            raise NotionAPIError(
                "Failed to list tasks",
                api_error=error.body,
                status_code=error.status,
            )
        except Exception as exc:
            logger.error("Unexpected error listing tasks: %s", exc)
            raise InternalError("Failed to list tasks", original_error=exc)

    def _build_list_filters(
        self,
        request: ListTasksRequest,
        property_mappings: Dict[str, str],
    ) -> Optional[dict[str, Any]]:
        """Construct Notion filter payload based on request parameters."""
        filters: List[dict[str, Any]] = []

        if request.status:
            filters.append({
                "property": property_mappings["status"],
                "status": {"equals": request.status},
            })

        if request.priority:
            filters.append({
                "property": property_mappings["priority"],
                "select": {"equals": request.priority},
            })

        if request.assignee:
            filters.append({
                "property": property_mappings["assignee"],
                "people": {"contains": request.assignee},
            })

        if request.due_date_from or request.due_date_to:
            date_filter: dict[str, Any] = {
                "property": property_mappings["due_date"],
                "date": {},
            }
            if request.due_date_from:
                date_filter["date"]["on_or_after"] = request.due_date_from.isoformat()
            if request.due_date_to:
                date_filter["date"]["on_or_before"] = request.due_date_to.isoformat()
            filters.append(date_filter)

        if request.project_id:
            filters.append({
                "property": property_mappings["project"],
                "relation": {"contains": request.project_id},
            })

        if not filters:
            return None
        if len(filters) == 1:
            return filters[0]
        return {"and": filters}

    def _build_sort_params(
        self,
        request: ListTasksRequest,
        property_mappings: Dict[str, str],
    ) -> List[dict[str, Any]]:
        """Map request sorting into Notion sorts payload."""
        direction = request.order
        if request.sort_by in {"created_time", "last_edited_time"}:
            return [{"timestamp": request.sort_by, "direction": direction}]

        property_name = property_mappings.get(request.sort_by, request.sort_by)
        return [{"property": property_name, "direction": direction}]

    def _map_page_to_summary(
        self,
        page: dict[str, Any],
        property_mappings: Dict[str, str],
    ) -> TaskSummary:
        """Convert raw Notion page into TaskSummary DTO."""
        properties = page.get("properties", {})
        title_property = properties.get(property_mappings["title"], {})
        due_property = properties.get(property_mappings["due_date"], {})
        status_property = properties.get(property_mappings["status"], {})
        priority_property = properties.get(property_mappings["priority"], {})
        assignee_property = properties.get(property_mappings["assignee"], {})

        return TaskSummary(
            notion_task_id=page.get("id"),
            title=self._extract_title(title_property),
            status=self._extract_status(status_property),
            priority=self._extract_select(priority_property),
            due_date=self._extract_date(due_property),
            assignees=self._extract_people(assignee_property),
            created_time=datetime.fromisoformat(page["created_time"].replace("Z", "+00:00")),
            last_edited_time=datetime.fromisoformat(page["last_edited_time"].replace("Z", "+00:00")),
            url=page.get("url", ""),
        )

    def _extract_title(self, property_payload: dict[str, Any]) -> str:
        """Extract title text from Notion title property."""
        title_items = property_payload.get("title", [])
        if not title_items:
            return "Untitled"
        first_item = title_items[0]
        return first_item.get("plain_text") or first_item.get("text", {}).get("content", "Untitled")

    def _extract_status(self, property_payload: dict[str, Any]) -> Optional[str]:
        """Extract status/select name from property payload."""
        status = property_payload.get("status")
        if status:
            return status.get("name")
        select = property_payload.get("select")
        if select:
            return select.get("name")
        return None

    def _extract_select(self, property_payload: dict[str, Any]) -> Optional[str]:
        """Extract select property value."""
        select = property_payload.get("select")
        if select:
            return select.get("name")
        return None

    def _extract_date(self, property_payload: dict[str, Any]) -> Optional[datetime]:
        """Extract datetime from Notion date property."""
        date_payload = property_payload.get("date")
        if date_payload and date_payload.get("start"):
            return datetime.fromisoformat(date_payload["start"].replace("Z", "+00:00"))
        return None

    def _extract_people(self, property_payload: dict[str, Any]) -> List[str]:
        """Extract assignee names or IDs from people property."""
        people = property_payload.get("people") or []
        assignees = []
        for person in people:
            assignees.append(person.get("name") or person.get("id", ""))
        return [name for name in assignees if name]

    @with_retry(
        max_retries=4,
        initial_delay=1.0,
        max_delay=8.0,
        jitter_factor=0.2,
    )
    async def update_task(
        self,
        task_id: str,
        request: UpdateTaskRequest,
        property_mappings: Optional[Dict[str, str]] = None,
    ) -> UpdateTaskResponse:
        """Update task properties in Notion."""
        try:
            client = await self._get_client()
            resolved_mappings = self._resolve_property_mappings(property_mappings)

            # Handle assignee resolution if needed
            resolved_assignee_id = None
            if request.assignee_id:
                if not self._user_mapping_service:
                    # For backward compatibility and testing, allow assignee_id to be used directly
                    # when user mapping service is not configured
                    # In production, the user mapping service should be configured
                    resolved_assignee_id = request.assignee_id
                else:
                    resolved_assignee_id = await self._user_mapping_service.resolve_notion_user_id(
                        platform="web",
                        platform_user_id=request.assignee_id
                    )

            # Build update properties with resolved assignee ID
            properties = self._build_update_properties(request, resolved_mappings, resolved_assignee_id)

            if not properties:
                raise ValidationError("No fields to update")

            page = await client.pages.update(page_id=task_id, properties=properties)

            return UpdateTaskResponse(
                notion_task_id=page["id"],
                notion_task_url=page.get("url", ""),
                updated_at=datetime.fromisoformat(page["last_edited_time"].replace("Z", "+00:00")),
                status=self._extract_status(
                    page.get("properties", {}).get(resolved_mappings["status"], {})
                ),
                priority=self._extract_select(
                    page.get("properties", {}).get(resolved_mappings["priority"], {})
                ),
                due_date=self._extract_date(
                    page.get("properties", {}).get(resolved_mappings["due_date"], {})
                ),
            )

        except APIResponseError as error:
            if error.status == 404:
                raise NotFoundError("task", task_id)
            if error.status == 400:
                raise ValidationError(
                    f"Invalid task update: {error.body.get('message', 'Bad request')}",
                    details=error.body,
                )
            raise NotionAPIError(
                "Failed to update task",
                api_error=error.body,
                status_code=error.status,
            )
        except Exception as exc:
            logger.error("Unexpected error updating task %s: %s", task_id, exc)
            raise InternalError("Failed to update task", original_error=exc)

    def _build_update_properties(
        self,
        request: UpdateTaskRequest,
        property_mappings: Dict[str, str],
        resolved_assignee_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build Notion properties payload for updates."""
        properties: Dict[str, Any] = {}

        if request.status:
            properties[property_mappings["status"]] = {"status": {"name": request.status}}

        if request.priority:
            properties[property_mappings["priority"]] = {
                "select": {"name": request.priority}
            }

        if request.due_date:
            properties[property_mappings["due_date"]] = {
                "date": {"start": request.due_date.isoformat()}
            }

        # Use the resolved_assignee_id that was already obtained in the calling method
        if resolved_assignee_id:
            properties[property_mappings["assignee"]] = {
                "people": [{"id": resolved_assignee_id}]
            }

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

    @with_retry(
        max_retries=4,
        initial_delay=1.0,
        max_delay=8.0,
        jitter_factor=0.2
    )
    async def delete_task(self, task_id: str) -> None:
        """
        Delete a task in Notion by archiving it.

        Args:
            task_id: Notion task ID to delete

        Raises:
            NotFoundError: If task not found
            NotionAPIError: If Notion API call fails
            InternalError: For unexpected errors
        """
        try:
            # Get client
            client = await self._get_client()

            # Update the page with archived: true (this is how Notion handles deletion)
            await client.pages.update(
                page_id=task_id,
                archived=True
            )

        except APIResponseError as e:
            # Map Notion API errors to domain errors
            if e.status == 404:
                raise NotFoundError("task", task_id)
            elif e.status == 400:
                raise ValidationError(
                    f"Invalid task ID: {e.body.get('message', 'Bad request')}",
                    field=e.body.get('field')
                )
            else:
                raise NotionAPIError(
                    f"Failed to delete task: {str(e)}",
                    api_error=e.body,
                    status_code=e.status
                )

        except Exception as e:
            logger.error(f"Unexpected error deleting task {task_id}: {str(e)}")
            raise InternalError("Failed to delete task", original_error=e)
