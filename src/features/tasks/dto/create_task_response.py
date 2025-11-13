"""Response DTO for creating tasks in Notion."""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field


class CreateTaskResponse(BaseModel):
    """Response model for newly created task."""
    
    notion_task_id: str = Field(..., description="Notion page ID for the task")
    notion_task_url: str = Field(..., description="URL to view the task in Notion")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "notion_task_id": "1a2b3c4d5e6f7890abcdef1234567890",
                "notion_task_url": "https://notion.so/1a2b3c4d5e6f7890abcdef1234567890",
                "created_at": "2023-07-20T15:30:00.000Z"
            }
        }
