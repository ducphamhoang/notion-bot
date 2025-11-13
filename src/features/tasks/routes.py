"""API routes for task management."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse

from src.features.tasks.dto.create_task_request import CreateTaskRequest
from src.features.tasks.dto.create_task_response import CreateTaskResponse
from src.features.tasks.services.notion_task_service import NotionTaskService
from src.core.errors.exceptions import DomainException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


async def get_task_service() -> NotionTaskService:
    """Dependency injection for task service."""
    return NotionTaskService()


@router.post(
    "/",
    response_model=CreateTaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task in Notion",
    description="Create a new task in the specified Notion database with optional properties like assignee, due date, and priority."
)
async def create_task(
    request: Request,
    task_data: CreateTaskRequest,
    task_service: Annotated[NotionTaskService, Depends(get_task_service)]
) -> CreateTaskResponse:
    """
    Create a new task in Notion database.
    
    - **title**: Task title (required, 1-200 characters)
    - **notion_database_id**: Target Notion database ID (required)
    - **assignee_id**: Platform user ID to assign (optional)
    - **due_date**: Due date for the task (optional)
    - **priority**: Task priority: Low, Medium, High (optional)
    - **properties**: Additional Notion properties (optional)
    
    Returns the created task details including Notion ID and URL.
    """
    return await task_service.create_task(task_data)


# Exception handlers are handled globally in main.py
