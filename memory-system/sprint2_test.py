#!/usr/bin/env python3
"""
Sprint 2: Test Voyage API + Store ONE Memory
Progressive development - minimal working implementation
"""

import os
import sys
from dotenv import load_dotenv
import voyageai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Load environment
load_dotenv()

VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:16333")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "voyage-4-lite")
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "1024"))

# Test memory from samples.md
TEST_MEMORY = {
    "title": "FastMCP: Minimal Python MCP Server",
    "description": "Use FastMCP for rapid prototyping MCP servers with minimal boilerplate.",
    "content": """Use FastMCP for rapid prototyping MCP servers with minimal boilerplate.

Example:
```python
from fastmcp import FastMCP

mcp = FastMCP("demo")

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b
```

Benefits over official SDK:
- Zero boilerplate (no transport setup)
- Auto tool registration via decorators
- Built-in stdio/SSE support

Use for: Prototypes, small servers, learning MCP
Skip for: Production servers needing custom transport""",
    "tags": ["#mcp", "#python", "#fastmcp", "#prototyping"],
    "memory_type": "procedural",
    "role": "backend"
}

def test_voyage_api():
    """Test Voyage API connection and embedding generation"""
    print(f"[1/4] Testing Voyage API ({EMBEDDING_MODEL})...")

    if not VOYAGE_API_KEY:
        print("ERROR: VOYAGE_API_KEY not found in .env")
        sys.exit(1)

    try:
        client = voyageai.Client(api_key=VOYAGE_API_KEY)
        result = client.embed(
            texts=["test embedding"],
            model=EMBEDDING_MODEL
        )
        embedding = result.embeddings[0]

        print(f"  ✓ API connection successful")
        print(f"  ✓ Model: {EMBEDDING_MODEL}")
        print(f"  ✓ Embedding dimension: {len(embedding)}")

        return client
    except Exception as e:
        print(f"ERROR: Voyage API test failed: {e}")
        sys.exit(1)

def test_qdrant_connection():
    """Test Qdrant connection"""
    print(f"\n[2/4] Testing Qdrant connection ({QDRANT_URL})...")

    try:
        client = QdrantClient(url=QDRANT_URL)
        collections = client.get_collections()

        print(f"  ✓ Qdrant connected")
        print(f"  ✓ Existing collections: {len(collections.collections)}")

        return client
    except Exception as e:
        print(f"ERROR: Qdrant connection failed: {e}")
        sys.exit(1)

def create_collection(qdrant_client, collection_name):
    """Create collection if not exists"""
    print(f"\n[3/4] Creating collection '{collection_name}'...")

    try:
        collections = qdrant_client.get_collections()
        existing = [c.name for c in collections.collections]

        if collection_name in existing:
            print(f"  ! Collection already exists, recreating...")
            qdrant_client.delete_collection(collection_name)

        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=Distance.COSINE
            )
        )

        print(f"  ✓ Collection created")
        return True
    except Exception as e:
        print(f"ERROR: Collection creation failed: {e}")
        sys.exit(1)

def store_memory(voyage_client, qdrant_client, collection_name):
    """Store ONE test memory"""
    print(f"\n[4/4] Storing test memory...")

    try:
        # Format document
        document = f"""**Title:** {TEST_MEMORY['title']}
**Description:** {TEST_MEMORY['description']}

**Content:** {TEST_MEMORY['content']}

**Tags:** {' '.join(TEST_MEMORY['tags'])}"""

        # Generate embedding
        print(f"  - Generating embedding...")
        result = voyage_client.embed(
            texts=[document],
            model=EMBEDDING_MODEL
        )
        embedding = result.embeddings[0]

        # Store in Qdrant
        print(f"  - Storing in Qdrant...")
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=1,
                    vector=embedding,
                    payload={
                        "title": TEST_MEMORY['title'],
                        "description": TEST_MEMORY['description'],
                        "content": TEST_MEMORY['content'],
                        "tags": TEST_MEMORY['tags'],
                        "memory_type": TEST_MEMORY['memory_type'],
                        "role": TEST_MEMORY['role']
                    }
                )
            ]
        )

        print(f"  ✓ Memory stored (ID: 1)")
        print(f"  ✓ Title: {TEST_MEMORY['title']}")
        print(f"  ✓ Role: {TEST_MEMORY['role']}")

        return True
    except Exception as e:
        print(f"ERROR: Memory storage failed: {e}")
        sys.exit(1)

def verify_storage(qdrant_client, collection_name):
    """Verify memory was stored correctly"""
    print(f"\nVerifying storage...")

    try:
        info = qdrant_client.get_collection(collection_name)
        print(f"  ✓ Collection: {collection_name}")
        print(f"  ✓ Points count: {info.points_count}")
        print(f"  ✓ Vectors count: {info.vectors_count}")

        # Retrieve the point
        point = qdrant_client.retrieve(
            collection_name=collection_name,
            ids=[1],
            with_payload=True,
            with_vectors=False
        )[0]

        print(f"\n  Retrieved memory:")
        print(f"    Title: {point.payload['title']}")
        print(f"    Description: {point.payload['description']}")
        print(f"    Tags: {', '.join(point.payload['tags'])}")

        return True
    except Exception as e:
        print(f"ERROR: Verification failed: {e}")
        return False

def main():
    print("=" * 60)
    print("Sprint 2: Voyage API Test + Store ONE Memory")
    print("=" * 60)

    # Test Voyage API
    voyage_client = test_voyage_api()

    # Test Qdrant
    qdrant_client = test_qdrant_connection()

    # Create collection (test collection for sprint 2)
    collection_name = "backend-patterns"  # Using role-based naming from v7 spec
    create_collection(qdrant_client, collection_name)

    # Store ONE memory
    store_memory(voyage_client, qdrant_client, collection_name)

    # Verify
    verify_storage(qdrant_client, collection_name)

    print("\n" + "=" * 60)
    print("✓ SPRINT 2 COMPLETE")
    print("=" * 60)
    print(f"\nView in Qdrant Dashboard: {QDRANT_URL}/dashboard")
    print(f"Collection: {collection_name}")
    print(f"Memory count: 1")

if __name__ == "__main__":
    main()
