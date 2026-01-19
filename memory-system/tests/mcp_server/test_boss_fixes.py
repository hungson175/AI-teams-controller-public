"""TDD tests for Boss-directed fixes.

These tests define the CORRECT behavior per Boss review.
They should FAIL initially (RED phase), then PASS after fixes (GREEN phase).
"""

import pytest
import json
from pydantic_core import ValidationError

from src.mcp_server.models import SearchMemoryInput, StoreMemoryInput, UpdateMemoryInput
from src.mcp_server.tools import mutation_tools


class TestBossFix1_QueryConstraints:
    """Test SearchMemoryInput.query accepts long queries (no max_length)."""

    def test_query_accepts_very_long_context(self):
        """Test query field accepts queries longer than 500 chars."""
        # Create a query with >500 chars (realistic AI agent search context)
        long_query = (
            "I need to find memories about implementing rate limiting for REST APIs in Node.js backend services. "
            "Specifically looking for patterns that handle distributed rate limiting across multiple server instances "
            "using Redis as a shared state store. The implementation should prevent thundering herd problems and "
            "gracefully handle Redis connection failures with fallback to local rate limiting. Also need examples "
            "of how to configure different rate limits for different API endpoints and user tiers (free vs premium). "
            "Additional context: working with Express.js framework, need middleware implementation, and must support "
            "both IP-based and user-ID-based rate limiting with configurable time windows and request limits."
        )

        assert len(long_query) > 500, "Test query must be >500 chars"

        # This should NOT raise validation error (should accept long queries)
        params = SearchMemoryInput(
            query=long_query,
            roles=["backend"],
            limit=20
        )

        assert params.query == long_query


class TestBossFix2_StoreMemoryMetadata:
    """Test StoreMemoryInput.metadata only accepts title, preview, content."""

    def test_metadata_accepts_only_three_fields(self):
        """Test metadata with ONLY title, preview, content is accepted."""
        # CORRECT metadata format per Boss
        params = StoreMemoryInput(
            document="""**Title:** Test Memory
**Description:** Test description

**Content:** Test content here

**Tags:** #test""",
            role="backend",  # Role is separate field, NOT in metadata
            metadata={
                "title": "Test Memory",
                "preview": "Test description",
                "content": "Full test content"
            }
        )

        assert params.role == "backend"
        assert "title" in params.metadata
        assert "preview" in params.metadata
        assert "content" in params.metadata
        assert len(params.metadata) == 3  # ONLY 3 fields

    def test_metadata_rejects_unauthorized_role_field(self):
        """Test metadata with 'role' field is rejected."""
        with pytest.raises(ValidationError):
            StoreMemoryInput(
                document="Test doc",
                metadata={
                    "title": "Test",
                    "preview": "Test preview",
                    "content": "Test content",
                    "role": "backend"  # UNAUTHORIZED field
                }
            )

    def test_metadata_rejects_unauthorized_tags_field(self):
        """Test metadata with 'tags' field is rejected."""
        with pytest.raises(ValidationError):
            StoreMemoryInput(
                document="Test doc",
                metadata={
                    "title": "Test",
                    "preview": "Test preview",
                    "content": "Test content",
                    "tags": ["test"]  # UNAUTHORIZED field
                }
            )

    def test_metadata_rejects_unauthorized_memory_type_field(self):
        """Test metadata with 'memory_type' field is rejected."""
        with pytest.raises(ValidationError):
            StoreMemoryInput(
                document="Test doc",
                metadata={
                    "title": "Test",
                    "preview": "Test preview",
                    "content": "Test content",
                    "memory_type": "episodic"  # UNAUTHORIZED field
                }
            )


class TestBossFix3_UpdateMemoryMetadata:
    """Test UpdateMemoryInput.metadata only accepts title, preview, content."""

    def test_metadata_accepts_only_three_fields(self):
        """Test metadata with ONLY title, preview, content is accepted."""
        params = UpdateMemoryInput(
            doc_id="12345678-1234-1234-1234-123456789012",
            document="Updated document content with proper length for validation",
            role="backend",  # Role is separate field, NOT in metadata
            metadata={
                "title": "Updated Title",
                "preview": "Updated preview",
                "content": "Updated full content"
            }
        )

        assert params.role == "backend"
        assert "title" in params.metadata
        assert "preview" in params.metadata
        assert "content" in params.metadata
        assert len(params.metadata) == 3  # ONLY 3 fields


class TestBossFix4_SearchDefaultLimit:
    """Test search_engine.py search function default limit = 50."""

    def test_search_default_limit_is_50(self):
        """Test search function defaults to limit=50 (not 20)."""
        from src.memory.search_engine import search
        import inspect

        # Get default value from function signature
        sig = inspect.signature(search)
        default_limit = sig.parameters['limit'].default

        assert default_limit == 50, f"Default limit should be 50, got {default_limit}"
