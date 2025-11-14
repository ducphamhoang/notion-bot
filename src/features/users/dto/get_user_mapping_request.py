"""Request DTO for querying user mappings."""

from pydantic import BaseModel, Field
from typing import Optional


class GetUserMappingRequest(BaseModel):
    """
    Request DTO for querying user mappings.
    """
    
    platform: Optional[str] = Field(
        None,
        description="Platform identifier (e.g., 'slack', 'teams', 'web')",
        example="slack"
    )
    
    platform_user_id: Optional[str] = Field(
        None,
        description="User ID in the platform (e.g., U012AB3CD in Slack)",
        example="U012AB3CD"
    )

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "platform": "slack",
                "platform_user_id": "U012AB3CD"
            }
        }