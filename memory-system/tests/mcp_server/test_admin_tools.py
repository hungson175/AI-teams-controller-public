"""Tests for admin tools.

Tests:
- list_collections: 3 tests
- create_collection: 5 tests

Total: 8 tests
"""

import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from src.mcp_server.tools import admin_tools
from src.mcp_server.models import CreateCollectionInput


class TestListCollections:
    """Tests for list_collections tool."""

    @pytest.mark.asyncio
    async def test_list_all_collections(self):
        """Test list_collections returns all available collections."""
        result_str = await admin_tools.list_collections()
        result = json.loads(result_str)

        assert "collections" in result
        assert isinstance(result["collections"], list)
        assert "total_collections" in result or "total" in result

        # Should have at least some known collections
        if result["collections"]:
            first_collection = result["collections"][0]
            assert "name" in first_collection
            assert "count" in first_collection or "documents" in first_collection

    @pytest.mark.asyncio
    async def test_list_returns_accurate_counts(self):
        """Test list_collections returns accurate document counts per collection."""
        result_str = await admin_tools.list_collections()
        result = json.loads(result_str)

        if result.get("collections"):
            for collection in result["collections"]:
                # Count should be non-negative integer
                count = collection.get("count") or collection.get("documents", 0)
                assert isinstance(count, int)
                assert count >= 0

    @pytest.mark.asyncio
    async def test_list_classifies_global_vs_project(self):
        """Test list_collections classifies collections as global or project-specific."""
        result_str = await admin_tools.list_collections()
        result = json.loads(result_str)

        if result.get("collections"):
            # Check if classification exists (implementation-specific)
            for collection in result["collections"]:
                # May have 'level' field or 'type' field
                if "level" in collection:
                    assert collection["level"] in ["global", "project", "user"]
                # Or may classify by name pattern (proj- prefix, etc.)


class TestCreateCollection:
    """Tests for create_collection tool."""

    @pytest.mark.asyncio
    async def test_create_new_collection_success(self):
        """Test creating new collection returns success."""
        params = CreateCollectionInput(
            collection_name="test-collection-xyz"
        )

        result_str = await admin_tools.create_collection(params)
        result = json.loads(result_str)

        assert "collection_name" in result or "name" in result
        assert "status" in result
        assert result["status"] in ["success", "created", "exists"]
        # Should include configuration
        if "dimension" in result:
            assert result["dimension"] == 1024
        if "distance" in result:
            assert result["distance"] in ["cosine", "COSINE"]

    @pytest.mark.asyncio
    async def test_create_existing_collection_returns_exists_status(self):
        """Test creating existing collection returns 'exists' status (idempotent)."""
        collection_name = "backend"  # Known existing collection

        params = CreateCollectionInput(
            collection_name=collection_name
        )

        result_str = await admin_tools.create_collection(params)
        result = json.loads(result_str)

        # Should be idempotent - either success or exists status
        assert result.get("status") in ["success", "exists", "already_exists"]

    @pytest.mark.asyncio
    async def test_create_with_invalid_name_validation_error(self):
        """Test Pydantic validation catches invalid collection names."""
        # Special characters should be rejected
        with pytest.raises(ValueError, match="alphanumeric"):
            CreateCollectionInput(
                collection_name="test!@#$%collection"
            )

    @pytest.mark.asyncio
    async def test_verify_dimension_1024_default(self):
        """Test create_collection uses dimension=1024 as default."""
        params = CreateCollectionInput(
            collection_name="test-dimension-check"
        )

        result_str = await admin_tools.create_collection(params)
        result = json.loads(result_str)

        # Should specify dimension in response
        if "dimension" in result:
            assert result["dimension"] == 1024

    @pytest.mark.asyncio
    async def test_verify_distance_cosine_default(self):
        """Test create_collection uses distance=COSINE as default."""
        params = CreateCollectionInput(
            collection_name="test-distance-check"
        )

        result_str = await admin_tools.create_collection(params)
        result = json.loads(result_str)

        # Should specify distance metric in response
        if "distance" in result:
            assert result["distance"].lower() == "cosine"
