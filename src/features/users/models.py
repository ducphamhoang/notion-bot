"""User mapping models for platform-to-Notion user ID mapping."""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from bson import ObjectId
from pydantic.json_schema import GetJsonSchemaHandler
from pydantic_core import core_schema


class PyObjectId(ObjectId):
    """Custom Pydantic field type for MongoDB ObjectId."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetJsonSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.str_schema(),
            ]),
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        if v is None:
            return ObjectId()
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        elif isinstance(v, ObjectId):
            return v
        else:
            raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler) -> Any:
        return handler(core_schema)


class UserMapping(BaseModel):
    """
    User mapping model for storing platform-to-Notion user ID mappings.

    This allows mapping platform users (e.g., Slack user IDs, Teams user IDs)
    to their corresponding Notion user IDs for assignee resolution.
    """

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    platform: str  # teams|slack|web
    platform_user_id: str  # User ID in the platform (e.g., U012AB3CD in Slack)
    notion_user_id: str  # User ID in Notion
    display_name: Optional[str] = None  # Display name for the user
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration for UserMapping model."""
        populate_by_name = True  # Allow both '_id' and 'id'
        arbitrary_types_allowed = True


class UserMappingInDB(UserMapping):
    """User mapping model with database-specific fields."""
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")