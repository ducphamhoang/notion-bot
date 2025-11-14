"""Response DTO for updating tasks."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UpdateTaskResponse(BaseModel):
    """Response model returned after updating a task."""

    notion_task_id: str = Field(..., description="Updated Notion task ID")
    notion_task_url: str = Field(..., description="URL to the updated task")
    updated_at: datetime = Field(..., description="Timestamp when the task was updated")
    status: Optional[str] = Field(None, description="Updated status value")
    priority: Optional[str] = Field(None, description="Updated priority value")
    due_date: Optional[datetime] = Field(None, description="Updated due date")

    class Config:
        json_encoders = {
            datetime: lambda value: value.isoformat()
        }
        schema_extra = {
            "example": {
                "notion_task_id": "1a2b3c4d5e6f7890abcdef1234567890",
                "notion_task_url": "https://notion.so/1a2b3c4d5e6f7890abcdef1234567890",
                "updated_at": "2025-01-12T09:45:00Z",
                "status": "Done",
                "priority": "High",
                "due_date": "2025-01-15T12:00:00Z"
            }
        }
