"""Admin tools for memory MCP server.

Implements:
- list_collections: List all collections with metadata
- create_collection: Dynamically create new collection
"""

import json
import logging

logger = logging.getLogger(__name__)

# Import server instance for decorator
from ..server import mcp
from ..models import CreateCollectionInput

# Import Sprint 3 functions
from src.memory.search_engine import _get_qdrant_client


@mcp.tool(
    name="list_collections",
    annotations={
        "title": "List Collections",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def list_collections() -> str:
    """List all available memory collections with metadata.

    No input parameters required.

    Returns:
        JSON string with collection list and counts
    """
    try:
        qdrant = _get_qdrant_client()

        # Get all collections from Qdrant
        collections_response = qdrant.get_collections()

        # Build collection list with metadata
        collections = []
        for collection in collections_response.collections:
            collection_name = collection.name

            # Get detailed collection info
            try:
                collection_info = qdrant.get_collection(collection_name)
                point_count = collection_info.points_count

                collections.append({
                    "name": collection_name,
                    "count": point_count,
                    "level": "global"  # Could classify based on name pattern
                })
            except Exception as e:
                logger.warning(f"Failed to get info for collection {collection_name}: {e}")
                collections.append({
                    "name": collection_name,
                    "count": 0,
                    "level": "global"
                })

        # Sort by name
        collections.sort(key=lambda x: x['name'])

        logger.info(f"Listed {len(collections)} collections")

        return json.dumps({
            "collections": collections,
            "total": len(collections)
        })

    except Exception as e:
        logger.error(f"Error in list_collections: {e}", exc_info=True)
        return json.dumps({
            "error": "List failed",
            "message": str(e),
            "type": "ListError"
        })


@mcp.tool(
    name="create_collection",
    annotations={
        "title": "Create Collection",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,  # Safe to call multiple times
        "openWorldHint": True
    }
)
async def create_collection(params: CreateCollectionInput) -> str:
    """Create a new memory collection dynamically.

    Uses hardcoded defaults:
    - dimension: 1024 (Voyage AI embedding size)
    - distance: COSINE

    Args:
        params: Validated input with collection_name

    Returns:
        JSON string with status and configuration
    """
    try:
        qdrant = _get_qdrant_client()

        collection_name = params.collection_name

        # Check if collection already exists
        try:
            collections_response = qdrant.get_collections()
            existing_names = [c.name for c in collections_response.collections]

            if collection_name in existing_names:
                logger.info(f"Collection {collection_name} already exists")
                return json.dumps({
                    "collection_name": collection_name,
                    "status": "exists",
                    "dimension": 1024,
                    "distance": "COSINE"
                })
        except Exception:
            pass

        # Create new collection with hardcoded config
        from qdrant_client.models import Distance, VectorParams

        qdrant.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1024,  # voyage-4-lite embedding size
                distance=Distance.COSINE
            )
        )

        logger.info(f"Created collection {collection_name} with dimension=1024, distance=COSINE")

        return json.dumps({
            "collection_name": collection_name,
            "status": "created",
            "dimension": 1024,
            "distance": "COSINE"
        })

    except Exception as e:
        logger.error(f"Error in create_collection: {e}", exc_info=True)
        return json.dumps({
            "error": "Create failed",
            "message": str(e),
            "type": "CreateError"
        })
