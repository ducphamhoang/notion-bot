"""DTO for creating a new Notion API token."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CreateTokenRequest(BaseModel):
    """Request model for creating a new Notion API token."""

    name: str = Field(
        description="Human-readable token name",
        min_length=1,
        max_length=100
    )
    token: str = Field(
        description="Raw Notion API token value (must start with 'secret_')"
    )
    description: Optional[str] = Field(
        None,
        description="Optional description for this token"
    )

    @field_validator('token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate that token starts with 'secret_' prefix."""
        if not v.startswith('secret_'):
            raise ValueError('Token must start with "secret_"')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate token name length."""
        v = v.strip()
        if not 1 <= len(v) <= 100:
            raise ValueError('Name must be between 1 and 100 characters')
        return v

    class Config:
        extra = "forbid"
        json_schema_extra = {
            "example": {
                "name": "Production API Token",
                "token": "secret_abc123xyz789...",
                "description": "Token for production Notion workspace"
            }
        }
