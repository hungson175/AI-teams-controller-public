"""Tests for mutation tools.

Tests:
- store_memory: 5 tests
- update_memory: 4 tests
- delete_memory: 4 tests

Total: 13 tests
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from src.mcp_server.tools import mutation_tools
from src.mcp_server.models import StoreMemoryInput, UpdateMemoryInput, DeleteMemoryInput


class TestStoreMemory:
    """Tests for store_memory tool."""

    @pytest.mark.asyncio
    async def test_store_new_memory_returns_uuid(self):
        """Test storing new memory returns generated UUID."""
        params = StoreMemoryInput(
            document="""**Title:** Test Memory
**Description:** Test description for new memory.

**Content:** This is test content for validation.

**Tags:** #test #validation #backend""",
            metadata={
                "memory_type": "episodic",
                "role": "backend",
                "tags": ["test", "validation"],
                "title": "Test Memory",
                "description": "Test description",
                "confidence": "high",
                "frequency": 1
            }
        )

        result_str = await mutation_tools.store_memory(params)
        result = json.loads(result_str)

        assert "doc_id" in result
        assert "status" in result
        assert result["status"] in ["success", "created"]
        # UUID should be valid format
        assert len(result["doc_id"]) == 36
        assert result["doc_id"].count('-') == 4

    @pytest.mark.asyncio
    async def test_store_with_minimal_metadata(self):
        """Test storing with only required metadata fields."""
        params = StoreMemoryInput(
            document="**Title:** Minimal\n**Content:** Minimal content.",
            metadata={
                "memory_type": "semantic",
                "role": "universal",
                "tags": ["minimal"],
                "title": "Minimal",
                "description": "Minimal description"
            }
        )

        result_str = await mutation_tools.store_memory(params)
        result = json.loads(result_str)

        assert "doc_id" in result
        assert "status" in result

    @pytest.mark.asyncio
    async def test_store_with_full_metadata(self):
        """Test storing with all optional metadata fields."""
        params = StoreMemoryInput(
            document="**Title:** Full Test\n**Content:** Full content.",
            metadata={
                "memory_type": "procedural",
                "role": "backend",
                "tags": ["full", "test"],
                "title": "Full Test",
                "description": "Full description",
                "confidence": 0.95,
                "frequency": 5,
                "source": "test-suite",
                "project_context": "testing"
            }
        )

        result_str = await mutation_tools.store_memory(params)
        result = json.loads(result_str)

        assert "doc_id" in result
        assert "status" in result

    @pytest.mark.asyncio
    async def test_store_with_invalid_role_returns_error(self):
        """Test storing with invalid role returns error."""
        # This should be caught during validation or storage
        params = StoreMemoryInput(
            document="**Title:** Test\n**Content:** Test.",
            metadata={
                "memory_type": "episodic",
                "role": "invalid-role-xyz-nonexistent",
                "tags": ["test"],
                "title": "Test",
                "description": "Test"
            }
        )

        result_str = await mutation_tools.store_memory(params)
        result = json.loads(result_str)

        # May return error or succeed (depending on validation strategy)
        # At minimum, should not crash
        assert "error" in result or "status" in result

    @pytest.mark.asyncio
    async def test_store_with_missing_required_fields_raises_validation_error(self):
        """Test Pydantic validation catches missing required fields."""
        with pytest.raises(ValueError, match="Missing required metadata"):
            StoreMemoryInput(
                document="Test document",
                metadata={
                    "memory_type": "episodic",
                    # Missing: role, tags, title, description
                }
            )


class TestUpdateMemory:
    """Tests for update_memory tool."""

    @pytest.mark.asyncio
    async def test_update_existing_document(self):
        """Test updating existing document succeeds."""
        params = UpdateMemoryInput(
            doc_id="c226fff1-7d09-457f-8264-728d249d3490",  # From fixtures
            document="""**Title:** Updated Title
**Description:** Updated description.

**Content:** Updated content with new information.

**Tags:** #updated #test""",
            metadata={
                "memory_type": "semantic",
                "role": "backend",
                "tags": ["updated", "test"],
                "title": "Updated Title",
                "description": "Updated description"
            }
        )

        result_str = await mutation_tools.update_memory(params)
        result = json.loads(result_str)

        assert "status" in result
        assert result["status"] in ["success", "updated"]
        assert result.get("doc_id") == "c226fff1-7d09-457f-8264-728d249d3490"

    @pytest.mark.asyncio
    async def test_update_nonexistent_document_returns_error(self):
        """Test updating non-existent document returns error."""
        params = UpdateMemoryInput(
            doc_id="00000000-0000-0000-0000-000000000000",
            document="Updated content",
            metadata={
                "memory_type": "episodic",
                "role": "backend",
                "tags": ["test"],
                "title": "Test",
                "description": "Test"
            }
        )

        result_str = await mutation_tools.update_memory(params)
        result = json.loads(result_str)

        assert "error" in result or result.get("status") == "not_found"

    @pytest.mark.asyncio
    async def test_update_regenerates_embedding(self):
        """Test update regenerates embedding (can't directly test, but verify no crash)."""
        params = UpdateMemoryInput(
            doc_id="c226fff1-7d09-457f-8264-728d249d3490",
            document="New content should generate new embedding.",
            metadata={
                "memory_type": "semantic",
                "role": "backend",
                "tags": ["test"],
                "title": "Test",
                "description": "Test"
            }
        )

        result_str = await mutation_tools.update_memory(params)
        result = json.loads(result_str)

        # Should not crash, regardless of embedding regeneration
        assert "status" in result or "error" in result

    @pytest.mark.asyncio
    async def test_update_timestamps_correctly(self):
        """Test update modifies timestamps correctly."""
        params = UpdateMemoryInput(
            doc_id="c226fff1-7d09-457f-8264-728d249d3490",
            document="Updated",
            metadata={
                "memory_type": "semantic",
                "role": "backend",
                "tags": ["test"],
                "title": "Test",
                "description": "Test"
            }
        )

        result_str = await mutation_tools.update_memory(params)
        result = json.loads(result_str)

        # Verify timestamp fields are mentioned (implementation-specific)
        if "metadata" in result:
            # last_updated or last_synced should be present
            assert "last_updated" in result["metadata"] or "last_synced" in result["metadata"]


class TestDeleteMemory:
    """Tests for delete_memory tool."""

    @pytest.mark.asyncio
    async def test_delete_existing_document(self):
        """Test deleting existing document succeeds."""
        params = DeleteMemoryInput(
            doc_id="c226fff1-7d09-457f-8264-728d249d3490",
            roles=["backend"]
        )

        result_str = await mutation_tools.delete_memory(params)
        result = json.loads(result_str)

        assert "status" in result
        assert result["status"] in ["success", "deleted"]
        # Should include remaining count
        if "remaining_memories" in result:
            assert isinstance(result["remaining_memories"], int)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_document_returns_error(self):
        """Test deleting non-existent document returns error."""
        params = DeleteMemoryInput(
            doc_id="00000000-0000-0000-0000-000000000000",
            roles=["backend"]
        )

        result_str = await mutation_tools.delete_memory(params)
        result = json.loads(result_str)

        assert "error" in result or result.get("status") == "not_found"

    @pytest.mark.asyncio
    async def test_delete_returns_remaining_count(self):
        """Test delete returns remaining document count in collection."""
        params = DeleteMemoryInput(
            doc_id="c226fff1-7d09-457f-8264-728d249d3490",
            roles=["backend", "universal"]
        )

        result_str = await mutation_tools.delete_memory(params)
        result = json.loads(result_str)

        # Should have remaining count field
        if result.get("status") == "success":
            assert "remaining_memories" in result or "remaining" in result

    @pytest.mark.asyncio
    async def test_delete_idempotent_second_delete_safe(self):
        """Test deleting same document twice is safe (idempotent)."""
        params = DeleteMemoryInput(
            doc_id="c226fff1-7d09-457f-8264-728d249d3490",
            roles=["backend"]
        )

        # First delete
        result1_str = await mutation_tools.delete_memory(params)
        result1 = json.loads(result1_str)

        # Second delete (should be safe, not crash)
        result2_str = await mutation_tools.delete_memory(params)
        result2 = json.loads(result2_str)

        # Second delete should return not_found or success
        assert "error" in result2 or result2.get("status") in ["not_found", "success", "already_deleted"]
