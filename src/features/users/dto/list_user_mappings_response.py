"""Response DTO for listing user mappings."""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from .user_mapping_response import UserMappingResponse


class ListUserMappingsResponse(BaseModel):
    """
    Response DTO for listing user mappings.
    """
    
    data: List[UserMappingResponse] = Field(
        ...,
        description="List of user mappings"
    )
    
    total: int = Field(
        ...,
        description="Total number of mappings",
        example=5
    )
    
    page: int = Field(
        default=1,
        description="Current page number",
        example=1
    )
    
    limit: int = Field(
        default=20,
        description="Number of mappings per page",
        example=20
    )
    
    has_more: bool = Field(
        default=False,
        description="Whether there are more mappings available"
    )

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "data": [
                    {
                        "id": "507f1f77bcf86cd799439011",
                        "platform": "slack",
                        "platform_user_id": "U012AB3CD",
                        "notion_user_id": "7e4229b0-4e65-4bbd-9908-712729897062",
                        "display_name": "John Doe",
                        "created_at": "2023-07-25T10:00:00Z",
                        "updated_at": "2023-07-25T10:00:00Z"
                    }
                ],
                "total": 1,
                "page": 1,
                "limit": 20,
                "has_more": False
            }
        }