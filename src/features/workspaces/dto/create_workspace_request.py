"""Request DTO for creating workspace mappings."""

from pydantic import BaseModel, Field, validator


class CreateWorkspaceRequest(BaseModel):
    """Request model for creating a new workspace mapping."""
    
    platform: str = Field(..., description="Platform name: teams|slack|web")
    platform_id: str = Field(..., description="Channel or workspace ID on platform") 
    notion_database_id: str = Field(..., description="Target Notion database UUID")
    name: str = Field(..., min_length=1, max_length=200, description="Human-readable workspace name")
    
    @validator('platform')
    def validate_platform(cls, v):
        """Validate platform is one of supported values."""
        valid_platforms = ['teams', 'slack', 'web']
        if v.lower() not in valid_platforms:
            raise ValueError(f"Platform must be one of: {', '.join(valid_platforms)}")
        return v.lower()
    
    @validator('notion_database_id')
    def validate_notion_database_id(cls, v):
        """Validate Notion database ID format."""
        import re
        # Notion database IDs are 32-character UUIDs with dashes removed
        if not re.match(r'^[a-f0-9]{32}$', v):
            raise ValueError("Invalid Notion database ID format")
        return v
    
    class Config:
        extra = "forbid"
        schema_extra = {
            "example": {
                "platform": "web",
                "platform_id": "default_workspace",
                "notion_database_id": "1a2b3c4d5e6f7890abcdef1234567890",
                "name": "My Project Workspace"
            }
        }
