#!/usr/bin/env python3
"""
Mini Search Engine for Two-Stage Memory Retrieval (Sprint 3)

Provides 3 core functions:
- search(): Preview-only search (snippets like Google)
- fetch(): Single document retrieval
- batch_fetch(): Multiple documents across collections
"""

import os
from typing import List, Dict, Tuple
from collections import defaultdict
from dotenv import load_dotenv
import voyageai
from qdrant_client import QdrantClient

load_dotenv()

# Global clients (initialized once)
_qdrant_client = None
_voyage_client = None

def _get_qdrant_client():
    """Get or create Qdrant client singleton"""
    global _qdrant_client
    if _qdrant_client is None:
        url = os.getenv('QDRANT_URL', 'http://localhost:16333')
        _qdrant_client = QdrantClient(url=url)
    return _qdrant_client

def _get_voyage_client():
    """Get or create Voyage AI client singleton"""
    global _voyage_client
    if _voyage_client is None:
        api_key = os.getenv('VOYAGE_API_KEY')
        if not api_key:
            raise ValueError("VOYAGE_API_KEY not found in environment")
        _voyage_client = voyageai.Client(api_key=api_key)
    return _voyage_client


def search(query: str, collection: str, limit: int = 50,
           qdrant_client=None, voyage_client=None) -> List[Dict]:
    """
    Search for memories and return preview-only results (like Google search results).

    Args:
        query: Search query text
        collection: Qdrant collection name (role)
        limit: Maximum number of results (default: 20)
        qdrant_client: Optional Qdrant client (for testing)
        voyage_client: Optional Voyage client (for testing)

    Returns:
        List of preview dictionaries with: id, title, preview, score
        Does NOT include full content field.

    Example:
        >>> results = search("rate limiting", "backend", limit=5)
        >>> print(results[0])
        {'id': 1, 'title': 'Rate Limiting Pattern', 'preview': '...', 'score': 0.95}
    """
    try:
        # Get clients (use provided or create)
        qdrant = qdrant_client or _get_qdrant_client()
        voyage = voyage_client or _get_voyage_client()

        # Generate embedding from query
        model = os.getenv('EMBEDDING_MODEL', 'voyage-4-lite')
        result = voyage.embed(texts=[query], model=model)
        query_vector = result.embeddings[0]

        # Search in Qdrant using query_points (NOT search)
        search_result = qdrant.query_points(
            collection_name=collection,
            query=query_vector,  # Note: 'query' not 'query_vector'
            limit=limit,
            with_payload=True,
            with_vectors=False
        )

        # Convert to preview objects (no content!)
        previews = []
        for point in search_result.points:
            previews.append({
                'id': point.id,
                'title': point.payload.get('title', ''),
                'preview': point.payload.get('preview', ''),
                'score': point.score
            })

        # Sort by score (highest first)
        previews.sort(key=lambda x: x['score'], reverse=True)

        return previews

    except Exception as e:
        # Return empty list on error (collection not found, etc.)
        return []


def fetch(doc_id: int, collection: str, qdrant_client=None) -> Dict:
    """
    Fetch full document content for a single memory.

    Args:
        doc_id: Document ID to retrieve
        collection: Qdrant collection name (role)
        qdrant_client: Optional Qdrant client (for testing)

    Returns:
        Full document dictionary with: id, title, preview, content

    Raises:
        ValueError: If document or collection not found

    Example:
        >>> doc = fetch(1, "backend")
        >>> print(doc['content'][:100])  # Full content available
    """
    try:
        qdrant = qdrant_client or _get_qdrant_client()

        # Retrieve from Qdrant
        points = qdrant.retrieve(
            collection_name=collection,
            ids=[doc_id],
            with_payload=True,
            with_vectors=False
        )

        if not points:
            raise ValueError(f"Document {doc_id} not found in collection {collection}")

        point = points[0]
        return {
            'id': point.id,
            'title': point.payload.get('title', ''),
            'preview': point.payload.get('preview', ''),
            'content': point.payload.get('content', '')
        }

    except ValueError:
        raise  # Re-raise ValueError as-is
    except Exception as e:
        raise ValueError(f"Collection {collection} not found or error: {e}")


def batch_fetch(doc_refs: List[Tuple[int, str]], qdrant_client=None) -> List[Dict]:
    """
    Fetch multiple documents across different collections efficiently.

    Args:
        doc_refs: List of (doc_id, collection) tuples
                  Example: [(1, "backend"), (2, "qa"), (3, "backend")]
        qdrant_client: Optional Qdrant client (for testing)

    Returns:
        List of full document dictionaries with: id, collection, title, preview, content
        Preserves input order. Skips non-existent documents without error.

    Example:
        >>> docs = batch_fetch([(1, "backend"), (5, "qa")])
        >>> print(docs[0]['collection'])  # "backend"
        >>> print(docs[1]['collection'])  # "qa"
    """
    if not doc_refs:
        return []

    try:
        qdrant = qdrant_client or _get_qdrant_client()

        # Group by collection for efficiency
        # {collection: [doc_ids]}
        collection_groups = defaultdict(list)
        for doc_id, collection in doc_refs:
            collection_groups[collection].append(doc_id)

        # Fetch from each collection
        # {(doc_id, collection): doc_dict}
        fetched_docs = {}

        for collection, doc_ids in collection_groups.items():
            try:
                points = qdrant.retrieve(
                    collection_name=collection,
                    ids=doc_ids,
                    with_payload=True,
                    with_vectors=False
                )

                for point in points:
                    key = (point.id, collection)
                    fetched_docs[key] = {
                        'id': point.id,
                        'collection': collection,
                        'title': point.payload.get('title', ''),
                        'preview': point.payload.get('preview', ''),
                        'content': point.payload.get('content', '')
                    }
            except Exception:
                # Skip collections that don't exist or have errors
                continue

        # Reconstruct in input order (skip missing docs)
        results = []
        for doc_id, collection in doc_refs:
            key = (doc_id, collection)
            if key in fetched_docs:
                results.append(fetched_docs[key])

        return results

    except Exception:
        # Return empty list on catastrophic error
        return []
