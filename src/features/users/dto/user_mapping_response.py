"""Response DTO for user mappings."""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class UserMappingResponse(BaseModel):
    """
    Response DTO for user mapping operations.
    """
    
    id: str = Field(
        ..., 
        description="Database ID of the user mapping",
        example="507f1f77bcf86cd799439011"
    )
    
    platform: str = Field(
        ..., 
        description="Platform identifier (e.g., 'slack', 'teams', 'web')",
        example="slack"
    )
    
    platform_user_id: str = Field(
        ..., 
        description="User ID in the platform (e.g., U012AB3CD in Slack)",
        example="U012AB3CD"
    )
    
    notion_user_id: str = Field(
        ..., 
        description="Corresponding Notion user ID",
        example="7e4229b0-4e65-4bbd-9908-712729897062"
    )
    
    display_name: Optional[str] = Field(
        None,
        description="Display name for the user (optional)",
        example="John Doe"
    )
    
    created_at: datetime = Field(
        ...,
        description="Timestamp when the mapping was created"
    )
    
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the mapping was last updated"
    )

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "id": "507f1f77bcf86cd799439011",
                "platform": "slack",
                "platform_user_id": "U012AB3CD",
                "notion_user_id": "7e4229b0-4e65-4bbd-9908-712729897062",
                "display_name": "John Doe",
                "created_at": "2023-07-25T10:00:00Z",
                "updated_at": "2023-07-25T10:00:00Z"
            }
        }