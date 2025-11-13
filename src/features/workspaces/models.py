"""MongoDB schema models for workspaces."""

from datetime import datetime
from typing import Optional, Annotated, Any
from pydantic import BaseModel, Field
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema
from bson import ObjectId


class _ObjectIdPydanticAnnotation:
    """Pydantic annotation for ObjectId validation and serialization."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """Generate Pydantic core schema for ObjectId."""
        def validate_from_str(value: str) -> ObjectId:
            if isinstance(value, ObjectId):
                return value
            if isinstance(value, str) and len(value) == 24:
                try:
                    return ObjectId(value)
                except Exception:
                    raise ValueError(f"Invalid ObjectId: {value}")
            raise ValueError(f"Invalid ObjectId type: {type(value)}")

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(
                lambda instance: str(instance)
            ),
        )


# Pydantic V2 compatible ObjectId type
PydanticObjectId = Annotated[ObjectId, _ObjectIdPydanticAnnotation]


class Workspace(BaseModel):
    """Workspace model for platform-to-Notion database mappings."""

    id: PydanticObjectId = Field(alias="_id", description="MongoDB document ID")
    platform: str = Field(description="Platform name: teams|slack|web")
    platform_id: str = Field(description="Channel or workspace ID on platform")
    notion_database_id: str = Field(description="Target Notion database UUID")
    name: str = Field(description="Human-readable workspace name")
    property_mappings: dict = Field(
        default_factory=lambda: {
            "title": "Name",
            "due_date": "Due Date",
            "priority": "Priority",
            "assignee": "Assignee",
            "status": "Status"
        },
        description="Mapping of standard field names to Notion property names"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }


class WorkspaceCreate(BaseModel):
    """Base model for creating workspaces."""
    platform: str = Field(description="Platform name: teams|slack|web")
    platform_id: str = Field(description="Channel or workspace ID on platform")
    notion_database_id: str = Field(description="Target Notion database UUID")
    name: str = Field(description="Human-readable workspace name")
    property_mappings: Optional[dict] = Field(
        default=None,
        description="Optional custom mapping of standard field names to Notion property names"
    )
    
    def to_create_model(self) -> dict:
        """Convert to dict for database insertion."""
        return self.dict()
    
    class Config:
        extra = "forbid"


class WorkspaceUpdate(BaseModel):
    """Base model for updating workspaces."""
    notion_database_id: Optional[str] = Field(None, description="Target Notion database UUID")
    name: Optional[str] = Field(None, description="Human-readable workspace name")
    property_mappings: Optional[dict] = Field(
        None,
        description="Custom mapping of standard field names to Notion property names"
    )
    
    class Config:
        extra = "forbid"


class WorkspaceResponse(Workspace):
    """Workspace model for API responses (same as base model)."""
    pass
