"""DTO for Notion API token responses."""

from datetime import datetime
from typing import Optional, Callable
from pydantic import BaseModel, Field

from src.features.tokens.models import NotionToken


class TokenResponse(BaseModel):
    """Response model for Notion API token."""

    id: str = Field(description="Token ID")
    name: str = Field(description="Human-readable token name")
    token_preview: str = Field(description="Masked token value showing last 6 characters")
    description: Optional[str] = Field(None, description="Optional token description")
    created_at: datetime = Field(description="Token creation timestamp")
    updated_at: datetime = Field(description="Token last update timestamp")
    is_active: bool = Field(description="Whether the token is active and can be used")

    @classmethod
    def from_token(cls, token: NotionToken, mask_token_fn: Callable[[str], str]) -> "TokenResponse":
        """Create TokenResponse from NotionToken model.
        
        Args:
            token: NotionToken model instance
            mask_token_fn: Function to mask the raw token value
            
        Returns:
            TokenResponse instance with masked token
        """
        return cls(
            id=str(token.id),
            name=token.name,
            token_preview=mask_token_fn(token.token),
            description=token.description,
            created_at=token.created_at,
            updated_at=token.updated_at,
            is_active=token.is_active
        )

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        json_schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "name": "Production API Token",
                "token_preview": "******...abc123",
                "description": "Token for production Notion workspace",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
                "is_active": True
            }
        }
