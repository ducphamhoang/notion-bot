"""MongoDB schema models for Notion API tokens."""

from datetime import datetime
from typing import Optional, Annotated, Any
from pydantic import BaseModel, Field, field_validator
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


PydanticObjectId = Annotated[ObjectId, _ObjectIdPydanticAnnotation]


class NotionToken(BaseModel):
    """Notion API token model for MongoDB storage."""

    id: PydanticObjectId = Field(alias="_id", description="MongoDB document ID")
    name: str = Field(description="Human-readable token name", min_length=1, max_length=100)
    token: str = Field(description="Raw Notion API token value")
    description: Optional[str] = Field(None, description="Optional token description")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Token creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Token last update timestamp")
    is_active: bool = Field(True, description="Whether the token is active and can be used")

    @field_validator('token')
    @classmethod
    def validate_token(cls, v: str) -> str:
        """Validate that token starts with 'secret_' prefix."""
        if not v.startswith('secret_'):
            raise ValueError('Token must start with "secret_"')
        return v

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate token name length."""
        v = v.strip()
        if not 1 <= len(v) <= 100:
            raise ValueError('Name must be between 1 and 100 characters')
        return v

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
