"""DTO for updating an existing Notion API token."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class UpdateTokenRequest(BaseModel):
    """Request model for updating a Notion API token."""

    name: Optional[str] = Field(
        None,
        description="Human-readable token name",
        min_length=1,
        max_length=100
    )
    description: Optional[str] = Field(
        None,
        description="Optional description for this token"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the token is active and can be used"
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate token name length if provided."""
        if v is not None:
            v = v.strip()
            if not 1 <= len(v) <= 100:
                raise ValueError('Name must be between 1 and 100 characters')
        return v

    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "name": "Updated Token Name",
                "description": "Updated description",
                "is_active": False
            }
        }
