"""Request DTO for listing and filtering tasks from Notion."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

_ALLOWED_SORT_FIELDS = {"created_time", "last_edited_time", "due_date", "priority"}


class ListTasksRequest(BaseModel):
    """Query parameters for listing tasks."""

    notion_database_id: str = Field(
        ...,
        min_length=32,
        max_length=36,
        description="Target Notion database ID (UUID with or without dashes)"
    )
    status: Optional[str] = Field(
        default=None,
        description="Filter by task status name"
    )
    assignee: Optional[str] = Field(
        default=None,
        description="Filter by Notion user ID assigned to the task"
    )
    due_date_from: Optional[datetime] = Field(
        default=None,
        description="Filter tasks with due dates on or after this datetime"
    )
    due_date_to: Optional[datetime] = Field(
        default=None,
        description="Filter tasks with due dates on or before this datetime"
    )
    priority: Optional[str] = Field(
        default=None,
        description="Filter by priority (Low, Medium, High)"
    )
    project_id: Optional[str] = Field(
        default=None,
        description="Filter by related project ID"
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number (1-indexed)"
    )
    limit: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of tasks per page (max 100)"
    )
    sort_by: str = Field(
        default="created_time",
        description="Field to sort by: created_time, last_edited_time, due_date, priority"
    )
    order: str = Field(
        default="asc",
        description="Sort order: asc or desc"
    )

    @validator("notion_database_id")
    def validate_database_id(cls, value: str) -> str:
        """Ensure Notion database ID is valid UUID format (with or without dashes)."""
        # Accept both formats: with dashes (36 chars) or without dashes (32 chars)
        if not re.fullmatch(r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}", value):
            if not re.fullmatch(r"[a-f0-9]{32}", value):
                raise ValueError("Invalid notion_database_id format (must be UUID with or without dashes)")
        return value

    @validator("priority")
    def validate_priority(cls, value: Optional[str]) -> Optional[str]:
        """Validate optional priority filter."""
        if value is None:
            return value
        normalized = value.capitalize()
        if normalized not in {"Low", "Medium", "High"}:
            raise ValueError("Priority must be Low, Medium, or High")
        return normalized

    @validator("order")
    def validate_order(cls, value: str) -> str:
        """Normalize and validate sort order."""
        normalized = value.lower()
        if normalized not in {"asc", "desc"}:
            raise ValueError("order must be 'asc' or 'desc'")
        return normalized

    @validator("sort_by")
    def validate_sort_by(cls, value: str) -> str:
        """Ensure sort field is supported."""
        normalized = value.lower()
        if normalized not in _ALLOWED_SORT_FIELDS:
            raise ValueError(
                f"sort_by must be one of: {', '.join(sorted(_ALLOWED_SORT_FIELDS))}"
            )
        return normalized

    @validator("status", "assignee", "project_id", pre=True)
    def strip_strings(cls, value: Optional[str]) -> Optional[str]:
        """Trim surrounding whitespace from optional string filters."""
        if value is None:
            return value
        stripped = value.strip()
        return stripped or None

    @validator("due_date_to")
    def validate_date_range(cls, value: Optional[datetime], values: dict) -> Optional[datetime]:
        """Ensure due_date_to is not before due_date_from."""
        start = values.get("due_date_from")
        if value and start and value < start:
            raise ValueError("due_date_to must be greater than or equal to due_date_from")
        return value

    class Config:
        extra = "forbid"
        schema_extra = {
            "example": {
                "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
                "status": "In Progress",
                "assignee": "user_001",
                "due_date_from": "2025-01-01T00:00:00Z",
                "due_date_to": "2025-01-31T23:59:59Z",
                "priority": "High",
                "project_id": "project_123",
                "page": 1,
                "limit": 20,
                "sort_by": "due_date",
                "order": "asc"
            }
        }
