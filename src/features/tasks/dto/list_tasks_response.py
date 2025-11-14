"""Response DTOs for listing tasks."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TaskSummary(BaseModel):
    """Normalized subset of task data returned from Notion."""

    notion_task_id: str = Field(..., description="Notion page ID")
    title: str = Field(..., description="Task title")
    status: Optional[str] = Field(None, description="Current task status")
    priority: Optional[str] = Field(None, description="Task priority")
    due_date: Optional[datetime] = Field(None, description="Due date if set")
    assignees: List[str] = Field(default_factory=list, description="List of assignee display names or IDs")
    created_time: datetime = Field(..., description="Notion created timestamp")
    last_edited_time: datetime = Field(..., description="Notion last edited timestamp")
    url: str = Field(..., description="Link to task in Notion")

    class Config:
        json_encoders = {
            datetime: lambda value: value.isoformat()
        }
        schema_extra = {
            "example": {
                "notion_task_id": "1a2b3c4d5e6f7890abcdef1234567890",
                "title": "Review pull request",
                "status": "In Progress",
                "priority": "High",
                "due_date": "2025-01-15T12:00:00Z",
                "assignees": ["Jane Doe"],
                "created_time": "2025-01-10T08:30:00Z",
                "last_edited_time": "2025-01-12T09:40:00Z",
                "url": "https://notion.so/1a2b3c4d5e6f7890abcdef1234567890"
            }
        }


class ListTasksResponse(BaseModel):
    """Paginated list response for tasks."""

    data: List[TaskSummary] = Field(..., description="Tasks returned for this page")
    page: int = Field(..., description="Current page (1-indexed)")
    limit: int = Field(..., description="Page size")
    total: int = Field(..., description="Number of tasks returned on this page")
    has_more: bool = Field(..., description="Whether more results are available")

    class Config:
        schema_extra = {
            "example": {
                "data": [TaskSummary.Config.schema_extra["example"]],
                "page": 1,
                "limit": 20,
                "total": 1,
                "has_more": False
            }
        }
