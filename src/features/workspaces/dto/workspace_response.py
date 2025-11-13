"""Response DTO for workspace operations."""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field
from src.features.workspaces.models import Workspace


class WorkspaceResponse(BaseModel):
    """Response model for workspace operations."""
    
    id: str = Field(..., description="MongoDB document ID")
    platform: str = Field(..., description="Platform name: teams|slack|web")
    platform_id: str = Field(..., description="Channel or workspace ID on platform")
    notion_database_id: str = Field(..., description="Target Notion database UUID")
    name: str = Field(..., description="Human-readable workspace name")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    @classmethod
    def from_workspace(cls, workspace: Workspace) -> "WorkspaceResponse":
        """Create response from workspace model."""
        return cls(
            id=str(workspace.id),
            platform=workspace.platform,
            platform_id=workspace.platform_id,
            notion_database_id=workspace.notion_database_id,
            name=workspace.name,
            created_at=workspace.created_at,
            updated_at=workspace.updated_at
        )
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "id": "60f7b3b3b3b3b3b3b3b3b3b3",
                "platform": "web",
                "platform_id": "default_workspace", 
                "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
                "name": "My Project Workspace",
                "created_at": "2023-07-20T15:30:00.000Z",
                "updated_at": "2023-07-20T15:30:00.000Z"
            }
        }


class WorkspaceListResponse(BaseModel):
    """Response model for listing multiple workspaces."""
    
    workspaces: list[WorkspaceResponse] = Field(default_factory=list, description="List of workspaces")
    count: int = Field(..., description="Total number of workspaces returned")
    
    class Config:
        schema_extra = {
            "example": {
                "workspaces": [
                    {
                        "id": "60f7b3b3b3b3b3b3b3b3b3b3",
                        "platform": "web",
                        "platform_id": "default_workspace",
                        "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
                        "name": "My Project Workspace",
                        "created_at": "2023-07-20T15:30:00.000Z",
                        "updated_at": "2023-07-20T15:30:00.000Z"
                    }
                ],
                "count": 1
            }
        }
