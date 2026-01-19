"""Pydantic models for MCP server input validation.

This module defines input schemas for all 8 MCP tools with proper validation,
following MCP best practices and Pydantic v2 patterns.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


class SearchMemoryInput(BaseModel):
    """Input model for search_memory tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    query: str = Field(
        ...,
        description="Search query text (e.g., 'API error handling patterns', 'React testing strategies')",
        min_length=2,
        max_length=500
    )
    roles: Optional[List[str]] = Field(
        default=None,
        description="List of roles to search (e.g., ['backend', 'universal']). If None, searches all roles."
    )
    limit: int = Field(
        default=20,
        description="Maximum results to return",
        ge=1,
        le=100
    )


class GetMemoryInput(BaseModel):
    """Input model for get_memory tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    doc_id: str = Field(
        ...,
        description="Document UUID to retrieve (e.g., 'a1b2c3d4-e5f6-7890-abcd-ef1234567890')",
        min_length=36,
        max_length=36
    )
    roles: Optional[List[str]] = Field(
        default=None,
        description="Roles to search in (optional). If None, searches all roles."
    )

    @field_validator('doc_id')
    @classmethod
    def validate_uuid_format(cls, v: str) -> str:
        """Validate UUID format (basic check for hyphenated structure)."""
        if v.count('-') != 4:
            raise ValueError("doc_id must be a valid UUID format with 4 hyphens")
        return v


class BatchGetMemoriesInput(BaseModel):
    """Input model for batch_get_memories tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    doc_ids: List[str] = Field(
        ...,
        description="List of document UUIDs to retrieve",
        min_items=1,
        max_items=50
    )
    roles: Optional[List[str]] = Field(
        default=None,
        description="Roles to search in (optional). If None, searches all roles."
    )

    @field_validator('doc_ids')
    @classmethod
    def validate_uuid_formats(cls, v: List[str]) -> List[str]:
        """Validate all UUIDs have correct format."""
        for uuid_str in v:
            if uuid_str.count('-') != 4:
                raise ValueError(f"Invalid UUID format: {uuid_str}")
        return v


class StoreMemoryInput(BaseModel):
    """Input model for store_memory tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    document: str = Field(
        ...,
        description="Full formatted memory text with Title, Description, Content, and Tags sections",
        min_length=10
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="Metadata including memory_type, role, tags, title, description, and optional fields"
    )

    @field_validator('metadata')
    @classmethod
    def validate_required_fields(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate required metadata fields are present."""
        required = ['memory_type', 'role', 'tags', 'title', 'description']
        missing = [field for field in required if field not in v]
        if missing:
            raise ValueError(f"Missing required metadata fields: {', '.join(missing)}")

        # Validate memory_type
        valid_types = ['episodic', 'semantic', 'procedural']
        if v['memory_type'] not in valid_types:
            raise ValueError(f"memory_type must be one of: {', '.join(valid_types)}")

        # Validate tags is a list
        if not isinstance(v['tags'], list):
            raise ValueError("tags must be a list")

        return v


class UpdateMemoryInput(BaseModel):
    """Input model for update_memory tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    doc_id: str = Field(
        ...,
        description="Document UUID to update",
        min_length=36,
        max_length=36
    )
    document: str = Field(
        ...,
        description="New formatted memory text",
        min_length=10
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="Updated metadata"
    )

    @field_validator('doc_id')
    @classmethod
    def validate_uuid_format(cls, v: str) -> str:
        """Validate UUID format."""
        if v.count('-') != 4:
            raise ValueError("doc_id must be a valid UUID format")
        return v

    @field_validator('metadata')
    @classmethod
    def validate_required_fields(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate required metadata fields."""
        required = ['memory_type', 'role', 'tags', 'title', 'description']
        missing = [field for field in required if field not in v]
        if missing:
            raise ValueError(f"Missing required metadata fields: {', '.join(missing)}")
        return v


class DeleteMemoryInput(BaseModel):
    """Input model for delete_memory tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    doc_id: str = Field(
        ...,
        description="Document UUID to delete",
        min_length=36,
        max_length=36
    )
    roles: Optional[List[str]] = Field(
        default=None,
        description="Roles to search in (optional). If None, searches all roles."
    )

    @field_validator('doc_id')
    @classmethod
    def validate_uuid_format(cls, v: str) -> str:
        """Validate UUID format."""
        if v.count('-') != 4:
            raise ValueError("doc_id must be a valid UUID format")
        return v


class CreateCollectionInput(BaseModel):
    """Input model for create_collection tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    collection_name: str = Field(
        ...,
        description="Collection name (e.g., 'product-owner', 'devops', 'backend')",
        min_length=1,
        max_length=100
    )

    @field_validator('collection_name')
    @classmethod
    def validate_collection_name(cls, v: str) -> str:
        """Validate collection name (alphanumeric + hyphens/underscores only)."""
        cleaned = v.replace('-', '').replace('_', '')
        if not cleaned.isalnum():
            raise ValueError(
                "Collection name must contain only alphanumeric characters, hyphens, and underscores"
            )
        return v.lower()  # Normalize to lowercase
