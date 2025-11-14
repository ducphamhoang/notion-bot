"""Request DTO for creating user mappings."""

from pydantic import BaseModel, Field
from typing import Optional


class CreateUserMappingRequest(BaseModel):
    """
    Request DTO for creating a user mapping between platform and Notion user IDs.
    
    This allows mapping platform users (e.g., Slack user IDs, Teams user IDs)
    to their corresponding Notion user IDs for assignee resolution.
    """
    
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

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "platform": "slack",
                "platform_user_id": "U012AB3CD",
                "notion_user_id": "7e4229b0-4e65-4bbd-9908-712729897062",
                "display_name": "John Doe"
            }
        }