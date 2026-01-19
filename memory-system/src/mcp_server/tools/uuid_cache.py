"""Shared UUID ↔ int mapping cache for all MCP tools.

This module provides a single, shared cache for bidirectional UUID ↔ int
mappings. All tools (search, mutation, admin) use this shared cache to
ensure consistency across the MCP server.
"""

import hashlib
from uuid import UUID
from typing import Optional, Dict

# Shared caches (module-level singletons)
_uuid_to_int_cache: Dict[str, int] = {}
_int_to_uuid_cache: Dict[int, str] = {}


def int_to_deterministic_uuid(doc_id: int) -> str:
    """Generate stable, deterministic UUID from int doc_id.

    Args:
        doc_id: Integer document ID (from Qdrant)

    Returns:
        UUID string (36 characters with hyphens)

    Side Effect:
        Caches the bidirectional mapping in module-level caches
    """
    namespace = "memory-doc"
    hash_input = f"{namespace}-{doc_id}".encode()
    hash_digest = hashlib.sha256(hash_input).digest()
    uuid_str = str(UUID(bytes=hash_digest[:16], version=4))

    # Cache bidirectional mapping
    _int_to_uuid_cache[doc_id] = uuid_str
    _uuid_to_int_cache[uuid_str] = doc_id

    return uuid_str


def uuid_to_int_id(uuid_str: str) -> Optional[int]:
    """Convert UUID back to int doc_id using shared cache.

    Args:
        uuid_str: UUID string to look up

    Returns:
        Integer document ID if found in cache, None otherwise
    """
    return _uuid_to_int_cache.get(uuid_str)
