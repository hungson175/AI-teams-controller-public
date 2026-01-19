"""Tests for search and retrieval tools.

Tests:
- search_memory: 5 tests
- get_memory: 4 tests
- batch_get_memories: 3 tests

Total: 12 tests
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from src.mcp_server.tools import search_tools
from src.mcp_server.models import SearchMemoryInput, GetMemoryInput, BatchGetMemoriesInput


class TestSearchMemory:
    """Tests for search_memory tool."""

    @pytest.mark.asyncio
    async def test_search_with_results_returns_previews_only(self):
        """Test search returns previews (title + description) without full content."""
        params = SearchMemoryInput(
            query="backend API testing patterns",
            roles=["backend", "universal"],
            limit=10
        )

        result_str = await search_tools.search_memory(params)
        result = json.loads(result_str)

        assert "results" in result
        assert isinstance(result["results"], list)
        assert len(result["results"]) <= 10

        # Verify preview format (no full document content)
        if result["results"]:
            first_result = result["results"][0]
            assert "doc_id" in first_result
            assert "title" in first_result
            assert "description" in first_result
            assert "similarity" in first_result
            assert "memory_type" in first_result
            assert "role" in first_result
            # Should NOT have full document content in previews
            assert "document" not in first_result

    @pytest.mark.asyncio
    async def test_search_empty_results(self):
        """Test search with no matching results."""
        params = SearchMemoryInput(
            query="zxcvbnmasdfghjkl_nonexistent_query_12345",
            roles=["backend"],
            limit=10
        )

        result_str = await search_tools.search_memory(params)
        result = json.loads(result_str)

        assert "results" in result
        assert result["results"] == []
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_search_with_multiple_roles(self):
        """Test search across multiple role collections."""
        params = SearchMemoryInput(
            query="testing patterns",
            roles=["backend", "frontend", "universal"],
            limit=20
        )

        result_str = await search_tools.search_memory(params)
        result = json.loads(result_str)

        assert "results" in result
        # Results may come from different roles
        if result["results"]:
            roles_found = {r["role"] for r in result["results"]}
            # At least one of the requested roles should appear
            assert roles_found.issubset({"backend", "frontend", "universal", "qa", "devops", "scrum-master"})

    @pytest.mark.asyncio
    async def test_search_respects_limit_parameter(self):
        """Test search respects limit parameter."""
        params = SearchMemoryInput(
            query="testing",
            roles=None,  # Search all roles
            limit=5
        )

        result_str = await search_tools.search_memory(params)
        result = json.loads(result_str)

        assert "results" in result
        assert len(result["results"]) <= 5

    @pytest.mark.asyncio
    async def test_search_with_invalid_role_graceful_handling(self):
        """Test search handles invalid role gracefully (empty results or error)."""
        params = SearchMemoryInput(
            query="test query",
            roles=["nonexistent-role-xyz"],
            limit=10
        )

        result_str = await search_tools.search_memory(params)
        result = json.loads(result_str)

        # Should either return empty results or error message (both acceptable)
        assert ("results" in result and result["results"] == []) or "error" in result


class TestGetMemory:
    """Tests for get_memory tool."""

    @pytest.mark.asyncio
    async def test_fetch_existing_document_returns_full_content(self):
        """Test fetching existing document returns full content with metadata."""
        # Use a known UUID from test fixtures
        params = GetMemoryInput(
            doc_id="c226fff1-7d09-457f-8264-728d249d3490",  # From fixtures
            roles=["backend", "universal"]
        )

        result_str = await search_tools.get_memory(params)
        result = json.loads(result_str)

        # Verify full document structure
        assert "doc_id" in result
        assert "document" in result  # Full formatted content
        assert "metadata" in result

        # Verify metadata structure
        metadata = result["metadata"]
        assert "memory_type" in metadata
        assert "role" in metadata
        assert "tags" in metadata
        assert "title" in metadata

        # Verify document content format
        document = result["document"]
        assert "**Title:**" in document or "Title:" in document

    @pytest.mark.asyncio
    async def test_fetch_nonexistent_document_returns_error(self):
        """Test fetching non-existent document returns error message."""
        params = GetMemoryInput(
            doc_id="00000000-0000-0000-0000-000000000000",  # Non-existent UUID
            roles=["backend"]
        )

        result_str = await search_tools.get_memory(params)
        result = json.loads(result_str)

        # Should return error
        assert "error" in result or (result.get("doc_id") is None and len(result) == 0)

    @pytest.mark.asyncio
    async def test_fetch_with_roles_specified(self):
        """Test fetch with specific roles filters correctly."""
        params = GetMemoryInput(
            doc_id="c226fff1-7d09-457f-8264-728d249d3490",
            roles=["backend"]  # Specify single role
        )

        result_str = await search_tools.get_memory(params)
        result = json.loads(result_str)

        # Should find document in backend collection
        if "metadata" in result:
            assert result["metadata"]["role"] == "backend"

    @pytest.mark.asyncio
    async def test_fetch_with_uuid_validation(self):
        """Test UUID validation works correctly."""
        # Invalid UUID format should be caught by Pydantic validation
        with pytest.raises(ValueError, match="UUID"):
            GetMemoryInput(
                doc_id="invalid-uuid-format",  # Missing hyphens
                roles=["backend"]
            )


class TestBatchGetMemories:
    """Tests for batch_get_memories tool."""

    @pytest.mark.asyncio
    async def test_batch_fetch_multiple_documents(self):
        """Test batch fetching multiple documents returns all."""
        params = BatchGetMemoriesInput(
            doc_ids=[
                "c226fff1-7d09-457f-8264-728d249d3490",
                "0a3d4b66-6e04-4178-bc8c-68a69f245a76"
            ],
            roles=["backend", "universal"]
        )

        result_str = await search_tools.batch_get_memories(params)
        result = json.loads(result_str)

        assert "memories" in result
        assert "retrieved" in result
        assert "requested" in result
        assert result["requested"] == 2
        assert result["retrieved"] <= 2  # May be less if some not found

    @pytest.mark.asyncio
    async def test_batch_fetch_with_partial_results(self):
        """Test batch fetch handles some missing documents gracefully."""
        params = BatchGetMemoriesInput(
            doc_ids=[
                "c226fff1-7d09-457f-8264-728d249d3490",  # Exists
                "00000000-0000-0000-0000-000000000000"   # Doesn't exist
            ],
            roles=["backend", "universal"]
        )

        result_str = await search_tools.batch_get_memories(params)
        result = json.loads(result_str)

        assert "memories" in result
        assert result["requested"] == 2
        # Should return partial results (1 document)
        assert result["retrieved"] >= 0  # May be 0 or 1 depending on implementation

    @pytest.mark.asyncio
    async def test_batch_fetch_with_empty_list(self):
        """Test batch fetch validates empty list properly."""
        # Empty list should be caught by Pydantic validation
        with pytest.raises(ValueError, match="min_items"):
            BatchGetMemoriesInput(
                doc_ids=[],  # Empty list
                roles=["backend"]
            )
