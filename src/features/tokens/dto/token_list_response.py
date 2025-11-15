"""DTO for list of Notion API tokens."""

from typing import List
from pydantic import BaseModel, Field

from src.features.tokens.dto.token_response import TokenResponse


class TokenListResponse(BaseModel):
    """Response model for list of Notion API tokens."""

    tokens: List[TokenResponse] = Field(description="List of tokens")
    total: int = Field(description="Total number of tokens")

    class Config:
        json_schema_extra = {
            "example": {
                "tokens": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "name": "Production API Token",
                        "token_preview": "******...abc123",
                        "description": "Token for production Notion workspace",
                        "created_at": "2024-01-15T10:30:00Z",
                        "updated_at": "2024-01-15T10:30:00Z",
                        "is_active": True
                    }
                ],
                "total": 1
            }
        }
