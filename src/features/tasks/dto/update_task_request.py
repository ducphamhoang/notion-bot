"""Request DTO for updating tasks."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, root_validator, validator


class UpdateTaskRequest(BaseModel):
    """Body payload for PATCH /tasks/{id}."""

    status: Optional[str] = Field(
        default=None,
        description="New task status"
    )
    assignee_id: Optional[str] = Field(
        default=None,
        description="Notion user ID to assign to the task"
    )
    due_date: Optional[datetime] = Field(
        default=None,
        description="Updated due date"
    )
    priority: Optional[str] = Field(
        default=None,
        description="Updated priority value"
    )
    properties: Optional[dict] = Field(
        default=None,
        description="Raw Notion properties to merge for custom fields"
    )

    @validator("priority")
    def validate_priority(cls, value: Optional[str]) -> Optional[str]:
        """Validate optional priority update."""
        if value is None:
            return value
        normalized = value.capitalize()
        if normalized not in {"Low", "Medium", "High"}:
            raise ValueError("Priority must be Low, Medium, or High")
        return normalized

    @root_validator(pre=True)
    def ensure_at_least_one_field(cls, values: dict) -> dict:
        """Ensure payload contains at least one updatable field."""
        fields = [
            values.get("status"),
            values.get("assignee_id"),
            values.get("due_date"),
            values.get("priority"),
            values.get("properties"),
        ]
        has_value = any(
            field is not None and field != {}  # Treat empty dict as missing
            for field in fields
        )
        if not has_value:
            raise ValueError("At least one field must be provided for update")
        return values

    class Config:
        extra = "forbid"
        schema_extra = {
            "example": {
                "status": "Done",
                "priority": "High",
                "due_date": "2025-01-15T12:00:00Z"
            }
        }
