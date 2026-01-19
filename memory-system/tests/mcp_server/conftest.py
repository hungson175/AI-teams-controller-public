"""Pytest configuration for MCP server tests.

Creates test collections using MCP tools (not direct Qdrant access).
"""

import pytest
import asyncio

# Import MCP tools to create collections
from src.mcp_server.tools import admin_tools
from src.mcp_server.models import CreateCollectionInput


@pytest.fixture(scope="session", autouse=True)
def ensure_test_collections():
    """Create all test collections using MCP create_collection tool.

    This fixture runs once per test session and creates all required
    collections using the MCP server's create_collection tool (not direct
    Qdrant access). This ensures tests use MCP tools properly.
    """
    # Collections required for tests
    required_collections = [
        "backend",
        "frontend",
        "qa",
        "devops",
        "scrum-master",
        "tech-leader",
        "other-role"
    ]

    # Create event loop to run async code
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        for collection_name in required_collections:
            try:
                # Use MCP tool to create collection (idempotent - safe to call multiple times)
                loop.run_until_complete(
                    admin_tools.create_collection(
                        CreateCollectionInput(collection_name=collection_name)
                    )
                )
            except Exception as e:
                # If creation fails (e.g., already exists), continue
                # The tool is idempotent so this is expected
                pass
    finally:
        loop.close()
