"""Search and retrieval tools for memory MCP server.

Implements:
- search_memory: Semantic search returning previews
- get_memory: Fetch single full document
- batch_get_memories: Fetch multiple documents efficiently
"""

import json
import logging
from typing import List, Optional, Dict, Any
import hashlib
from uuid import UUID

logger = logging.getLogger(__name__)

# Import server instance for decorator
from ..server import mcp
from ..models import SearchMemoryInput, GetMemoryInput, BatchGetMemoriesInput

# Import Sprint 3 functions
from src.memory.search_engine import search, fetch, batch_fetch

# UUID ↔ int mapping (deterministic based on mcp-builder review recommendation)
_uuid_to_int_cache: Dict[str, int] = {}
_int_to_uuid_cache: Dict[int, str] = {}


def _int_to_deterministic_uuid(doc_id: int) -> str:
    """Generate stable, deterministic UUID from int doc_id."""
    namespace = "memory-doc"
    hash_input = f"{namespace}-{doc_id}".encode()
    hash_digest = hashlib.sha256(hash_input).digest()
    # Create UUID from first 16 bytes of hash
    uuid_str = str(UUID(bytes=hash_digest[:16], version=4))

    # Cache bidirectional mapping
    _int_to_uuid_cache[doc_id] = uuid_str
    _uuid_to_int_cache[uuid_str] = doc_id

    return uuid_str


def _uuid_to_int_id(uuid_str: str) -> Optional[int]:
    """Convert UUID back to int doc_id using cache."""
    return _uuid_to_int_cache.get(uuid_str)


@mcp.tool(
    name="search_memory",
    annotations={
        "title": "Search Memories",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def search_memory(params: SearchMemoryInput) -> str:
    """Search for memories using semantic search.

    Returns previews (title + description) only for two-stage retrieval.
    Use get_memory() to retrieve full content after reviewing previews.

    Args:
        params: Validated search parameters

    Returns:
        JSON string with search results
    """
    try:
        # Determine collections to search
        collections = params.roles if params.roles else ["backend", "frontend", "universal", "qa", "devops", "scrum-master"]

        # Search across all specified collections
        all_results = []
        for collection in collections:
            try:
                results = search(params.query, collection, params.limit)
                for result in results:
                    # Convert int ID to deterministic UUID
                    uuid_str = _int_to_deterministic_uuid(result['id'])
                    all_results.append({
                        "doc_id": uuid_str,
                        "title": result['title'],
                        "description": result['preview'],
                        "similarity": result['score'],
                        "memory_type": "semantic",  # Default
                        "tags": [],
                        "role": collection,
                        "created_at": "2026-01-01T00:00:00"
                    })
            except Exception:
                continue  # Skip collections that don't exist

        # Sort by similarity and apply global limit
        all_results.sort(key=lambda x: x['similarity'], reverse=True)
        all_results = all_results[:params.limit]

        return json.dumps({
            "results": all_results,
            "total": len(all_results),
            "message": f"Found {len(all_results)} memory previews. Use get_memory(doc_id) to retrieve full content."
        })

    except Exception as e:
        logger.error(f"Error in search_memory: {e}", exc_info=True)
        return json.dumps({
            "error": "Search failed",
            "message": str(e),
            "type": "SearchError"
        })


@mcp.tool(
    name="get_memory",
    annotations={
        "title": "Get Memory",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def get_memory(params: GetMemoryInput) -> str:
    """Retrieve full memory content by UUID.

    Args:
        params: Validated input with doc_id and optional roles

    Returns:
        JSON string with full document and metadata
    """
    try:
        # Convert UUID to int
        int_id = _uuid_to_int_id(params.doc_id)
        if int_id is None:
            return json.dumps({"error": "Document not found", "type": "NotFoundError"})

        # Determine collections to search
        collections = params.roles if params.roles else ["backend", "frontend", "universal", "qa", "devops", "scrum-master"]

        # Try each collection
        for collection in collections:
            try:
                doc = fetch(int_id, collection)
                return json.dumps({
                    "doc_id": params.doc_id,
                    "document": doc['content'],
                    "metadata": {
                        "memory_type": "semantic",
                        "role": collection,
                        "tags": [],
                        "title": doc['title'],
                        "confidence": "high",
                        "frequency": 1,
                        "created_at": "2026-01-01T00:00:00",
                        "last_synced": "2026-01-01T00:00:00",
                        "description": doc['preview']
                    }
                })
            except ValueError:
                continue  # Try next collection

        return json.dumps({"error": "Document not found", "type": "NotFoundError"})

    except Exception as e:
        logger.error(f"Error in get_memory: {e}", exc_info=True)
        return json.dumps({
            "error": "Fetch failed",
            "message": str(e),
            "type": "FetchError"
        })


@mcp.tool(
    name="batch_get_memories",
    annotations={
        "title": "Batch Get Memories",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def batch_get_memories(params: BatchGetMemoriesInput) -> str:
    """Retrieve multiple memories efficiently.

    Args:
        params: Validated input with list of doc_ids and optional roles

    Returns:
        JSON string with array of full documents
    """
    try:
        # Convert UUIDs to (int, collection) pairs
        doc_refs = []
        collections = params.roles if params.roles else ["backend", "frontend", "universal", "qa", "devops", "scrum-master"]

        for uuid_str in params.doc_ids:
            int_id = _uuid_to_int_id(uuid_str)
            if int_id is not None:
                # Try all collections
                for collection in collections:
                    doc_refs.append((int_id, collection))

        # Batch fetch
        docs = batch_fetch(doc_refs)

        # Convert to response format with UUIDs
        memories = []
        for doc in docs:
            uuid_str = _int_to_deterministic_uuid(doc['id'])
            memories.append({
                "doc_id": uuid_str,
                "document": doc['content'],
                "metadata": {
                    "memory_type": "semantic",
                    "role": doc['collection'],
                    "tags": [],
                    "title": doc['title'],
                    "confidence": "high",
                    "frequency": 1,
                    "created_at": "2026-01-01T00:00:00",
                    "last_synced": "2026-01-01T00:00:00",
                    "description": doc['preview']
                }
            })

        return json.dumps({
            "memories": memories,
            "retrieved": len(memories),
            "requested": len(params.doc_ids)
        })

    except Exception as e:
        logger.error(f"Error in batch_get_memories: {e}", exc_info=True)
        return json.dumps({
            "error": "Batch fetch failed",
            "message": str(e),
            "type": "BatchFetchError"
        })
