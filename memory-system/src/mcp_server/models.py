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
        description="Search query with full context. AI coding agents provide extensive, detailed search context describing exactly what they need.",
        min_length=32
    )
    roles: Optional[List[str]] = Field(
        default=None,
        description="List of roles to search (e.g., ['backend', 'frontend']). If None, searches all roles."
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
    role: str = Field(
        ...,
        description="Collection name / role (e.g., 'backend', 'frontend', 'qa'). Determines which collection to store in."
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="Metadata with ONLY 3 fields: title, preview, content. Role is specified separately, NOT in metadata."
    )

    @field_validator('metadata')
    @classmethod
    def validate_required_fields(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate metadata has ONLY title, preview, content (per Boss requirements)."""
        required = ['title', 'preview', 'content']
        missing = [field for field in required if field not in v]
        if missing:
            raise ValueError(f"Missing required metadata fields: {', '.join(missing)}")

        # Boss: Metadata ONLY has title, preview, content - nothing else
        allowed = {'title', 'preview', 'content'}
        extra = set(v.keys()) - allowed
        if extra:
            raise ValueError(f"Unauthorized metadata fields: {', '.join(extra)}. Only title, preview, content allowed.")

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
    role: str = Field(
        ...,
        description="Collection name / role (e.g., 'backend', 'frontend', 'qa'). Determines which collection to update in."
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="Updated metadata with ONLY 3 fields: title, preview, content"
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
        """Validate metadata has ONLY title, preview, content (per Boss requirements)."""
        required = ['title', 'preview', 'content']
        missing = [field for field in required if field not in v]
        if missing:
            raise ValueError(f"Missing required metadata fields: {', '.join(missing)}")

        # Boss: Metadata ONLY has title, preview, content - nothing else
        allowed = {'title', 'preview', 'content'}
        extra = set(v.keys()) - allowed
        if extra:
            raise ValueError(f"Unauthorized metadata fields: {', '.join(extra)}. Only title, preview, content allowed.")

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
