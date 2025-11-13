"""Request DTO for creating tasks in Notion."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class CreateTaskRequest(BaseModel):
    """Request model for creating a new task."""
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title"
    )
    notion_database_id: str = Field(
        ...,
        description="Target Notion database ID"
    )
    assignee_id: Optional[str] = Field(
        None,
        description="Platform user ID to assign to this task"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Due date for the task"
    )
    priority: Optional[str] = Field(
        None,
        description="Task priority: Low, Medium, High"
    )
    properties: Optional[dict] = Field(
        default_factory=dict,
        description="Additional Notion properties to set on the task"
    )
    
    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority values."""
        if v and v not in ['Low', 'Medium', 'High']:
            raise ValueError('Priority must be Low, Medium, or High')
        return v
    
    @validator('title')
    def validate_title(cls, v):
        """Validate title doesn't contain control characters."""
        if any(c < ' ' for c in v):
            raise ValueError('Title contains invalid characters')
        return v.strip()
    
    class Config:
        extra = "forbid"
        schema_extra = {
            "example": {
                "title": "Fix login bug",
                "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
                "assignee_id": "user_001",
                "due_date": "2023-07-25T00:00:00.000Z",
                "priority": "High",
                "properties": {
                    "Tags": {"multi_select": [{"name": "bug"}]},
                    "Project": {"relation": [{"id": "project-123"}]}
                }
            }
        }
