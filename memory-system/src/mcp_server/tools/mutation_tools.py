"""Mutation tools for memory MCP server.

Implements:
- store_memory: Create new memory with auto-generated UUID
- update_memory: Update existing memory (regenerates embedding)
- delete_memory: Delete memory by UUID
"""

import json
import logging
import hashlib
from uuid import UUID
from datetime import datetime
import os
import re

logger = logging.getLogger(__name__)

# Import server instance for decorator
from ..server import mcp
from ..models import StoreMemoryInput, UpdateMemoryInput, DeleteMemoryInput

# Import Sprint 3 functions
from src.memory.search_engine import _get_qdrant_client, _get_voyage_client

# Import shared UUID cache (shared across all MCP tools)
from .uuid_cache import int_to_deterministic_uuid as _int_to_deterministic_uuid
from .uuid_cache import uuid_to_int_id as _uuid_to_int_id


def _generate_next_id(collection: str, qdrant_client) -> int:
    """Generate next available ID for collection (timestamp-based for uniqueness)."""
    # Use timestamp in microseconds for unique ID
    import time
    return int(time.time() * 1_000_000)


def _parse_document(document: str) -> dict:
    """Parse formatted document to extract title and description.

    Expected format:
    **Title:** Memory Title
    **Description:** Brief description

    **Content:** Full content here

    **Tags:** #tag1 #tag2
    """
    # Extract title
    title_match = re.search(r'\*\*Title:\*\*\s*(.+?)(?:\n|$)', document, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else "Untitled"

    # Extract description for preview
    desc_match = re.search(r'\*\*Description:\*\*\s*(.+?)(?:\n\n|\n\*\*|$)', document, re.IGNORECASE | re.DOTALL)
    preview = desc_match.group(1).strip() if desc_match else document[:200]

    return {'title': title, 'preview': preview}


@mcp.tool(
    name="store_memory",
    annotations={
        "title": "Store Memory",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,  # Generates new UUID each time
        "openWorldHint": True
    }
)
async def store_memory(params: StoreMemoryInput) -> str:
    """Store a new memory in the vector database.

    Generates a new UUID, creates embedding, and stores in appropriate collection.

    Args:
        params: Validated input with document and metadata

    Returns:
        JSON string with UUID and status
    """
    try:
        qdrant = _get_qdrant_client()
        voyage = _get_voyage_client()

        # Extract collection from metadata
        collection = params.metadata['role']

        # Generate unique int ID (timestamp-based)
        int_id = _generate_next_id(collection, qdrant)

        # Generate deterministic UUID
        uuid_str = _int_to_deterministic_uuid(int_id)

        # Parse document to extract title and preview
        parsed = _parse_document(params.document)

        # Generate embedding from full document
        model = os.getenv('EMBEDDING_MODEL', 'voyage-4-lite')
        result = voyage.embed(texts=[params.document], model=model)
        vector = result.embeddings[0]

        # Prepare payload
        payload = {
            'title': parsed['title'],
            'preview': parsed['preview'],
            'content': params.document
        }

        # Store in Qdrant
        from qdrant_client.models import PointStruct
        qdrant.upsert(
            collection_name=collection,
            points=[PointStruct(id=int_id, vector=vector, payload=payload)]
        )

        logger.info(f"Stored memory {uuid_str} (int_id={int_id}) in collection {collection}")

        return json.dumps({
            "doc_id": uuid_str,
            "status": "created",
            "collection": collection,
            "title": parsed['title']
        })

    except Exception as e:
        logger.error(f"Error in store_memory: {e}", exc_info=True)
        return json.dumps({
            "error": "Store failed",
            "message": str(e),
            "type": "StoreError"
        })


@mcp.tool(
    name="update_memory",
    annotations={
        "title": "Update Memory",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,  # Same input = same result
        "openWorldHint": True
    }
)
async def update_memory(params: UpdateMemoryInput) -> str:
    """Update existing memory (regenerates embedding).

    Args:
        params: Validated input with doc_id, document, and metadata

    Returns:
        JSON string with status
    """
    try:
        qdrant = _get_qdrant_client()
        voyage = _get_voyage_client()

        # Convert UUID to int
        int_id = _uuid_to_int_id(params.doc_id)
        if int_id is None:
            return json.dumps({"error": "Document not found", "type": "NotFoundError"})

        # Extract collection from metadata
        collection = params.metadata['role']

        # Check if document exists
        try:
            points = qdrant.retrieve(
                collection_name=collection,
                ids=[int_id],
                with_payload=False,
                with_vectors=False
            )
            if not points:
                return json.dumps({"error": "Document not found", "type": "NotFoundError"})
        except Exception:
            return json.dumps({"error": "Document not found", "type": "NotFoundError"})

        # Parse document to extract title and preview
        parsed = _parse_document(params.document)

        # Generate new embedding
        model = os.getenv('EMBEDDING_MODEL', 'voyage-4-lite')
        result = voyage.embed(texts=[params.document], model=model)
        vector = result.embeddings[0]

        # Prepare payload
        payload = {
            'title': parsed['title'],
            'preview': parsed['preview'],
            'content': params.document
        }

        # Update in Qdrant (upsert with same ID)
        from qdrant_client.models import PointStruct
        qdrant.upsert(
            collection_name=collection,
            points=[PointStruct(id=int_id, vector=vector, payload=payload)]
        )

        logger.info(f"Updated memory {params.doc_id} (int_id={int_id}) in collection {collection}")

        return json.dumps({
            "doc_id": params.doc_id,
            "status": "updated",
            "metadata": {
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }
        })

    except Exception as e:
        logger.error(f"Error in update_memory: {e}", exc_info=True)
        return json.dumps({
            "error": "Update failed",
            "message": str(e),
            "type": "UpdateError"
        })


@mcp.tool(
    name="delete_memory",
    annotations={
        "title": "Delete Memory",
        "readOnlyHint": False,
        "destructiveHint": True,  # Permanently removes data
        "idempotentHint": True,  # Second delete is safe
        "openWorldHint": True
    }
)
async def delete_memory(params: DeleteMemoryInput) -> str:
    """Delete a memory by UUID.

    Args:
        params: Validated input with doc_id and optional roles

    Returns:
        JSON string with status and remaining count
    """
    try:
        qdrant = _get_qdrant_client()

        # Convert UUID to int
        int_id = _uuid_to_int_id(params.doc_id)
        if int_id is None:
            return json.dumps({"error": "Document not found", "type": "NotFoundError"})

        # Determine collections to try
        collections = params.roles if params.roles else ["backend", "frontend", "qa", "devops", "scrum-master", "tech-leader"]

        # Try deleting from each collection
        deleted_from = None
        for collection in collections:
            try:
                # Check if document exists
                points = qdrant.retrieve(
                    collection_name=collection,
                    ids=[int_id],
                    with_payload=False,
                    with_vectors=False
                )

                if points:
                    # Delete the document
                    qdrant.delete(
                        collection_name=collection,
                        points_selector=[int_id]
                    )
                    deleted_from = collection
                    break
            except Exception:
                continue

        if deleted_from is None:
            return json.dumps({"error": "Document not found", "type": "NotFoundError"})

        # Get remaining count in collection
        try:
            collection_info = qdrant.get_collection(deleted_from)
            remaining_count = collection_info.points_count
        except Exception:
            remaining_count = 0

        logger.info(f"Deleted memory {params.doc_id} (int_id={int_id}) from collection {deleted_from}")

        return json.dumps({
            "doc_id": params.doc_id,
            "status": "deleted",
            "collection": deleted_from,
            "remaining_memories": remaining_count
        })

    except Exception as e:
        logger.error(f"Error in delete_memory: {e}", exc_info=True)
        return json.dumps({
            "error": "Delete failed",
            "message": str(e),
            "type": "DeleteError"
        })
