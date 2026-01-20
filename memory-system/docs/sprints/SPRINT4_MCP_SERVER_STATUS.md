# Sprint 4: Existing 'memory' MCP Server Status

**Date:** 2026-01-19  
**Status:** Analysis Complete

---

## Existing 'memory' MCP Server Tools

The 'memory' MCP server is ALREADY RUNNING with **7 tools**:

### Read-Only Tools (3)
1. **search_memory**
   - Search for memories using semantic search
   - Returns previews (title + description) only
   - Input: query, roles (list), limit
   - Output: JSON with preview results

2. **get_memory**
   - Retrieve full memory content by ID
   - Input: doc_id, roles (optional)
   - Output: JSON with full memory content

3. **batch_get_memories**
   - Retrieve multiple memories by IDs efficiently
   - Input: doc_ids (list), roles (optional)
   - Output: JSON with all retrieved memories

### Write Tools (3)
4. **store_memory**
   - Store a new memory in the vector database
   - Input: document (formatted text), metadata (dict)
   - Output: JSON with doc_id and status

5. **update_memory**
   - Update existing memory (regenerates embedding)
   - Input: doc_id, document, metadata
   - Output: JSON with update confirmation

6. **delete_memory**
   - Delete a memory by ID
   - Input: doc_id, roles (optional)
   - Output: JSON with deletion confirmation

### Utility Tools (1)
7. **list_collections**
   - List all available memory collections with counts
   - Input: (none)
   - Output: JSON with collection information

**Verification:** list_collections returned 15 collections:
- 9 global collections (universal, backend, frontend, etc.)
- 6 project-specific collections

---

## What's Missing: Create Collection Tool

**Analysis:** The existing server auto-creates collections from a hardcoded list (ROLE_COLLECTIONS) on startup, but there's **NO tool to dynamically create new collections** at runtime.

**Gap:** Users cannot:
- Create custom role collections
- Create project-specific collections on demand
- Extend the system with new collection types without server restart

---

## Sprint 4 Scope (REVISED)

### Goal
Add a `create_collection` tool to the existing 'memory' MCP server.

### Tool Specification: create_collection

**Purpose:** Dynamically create new memory collections

**Input Schema:**
```python
{
    "collection_name": str,     # Collection name (e.g., "project-X", "role-Y")
    "dimension": int,           # Vector dimension (default: 1024 for Voyage)
    "distance": str             # Distance metric: "cosine", "euclid", "dot" (default: "cosine")
}
```

**Output:**
```json
{
    "collection_name": "project-X",
    "status": "success",
    "dimension": 1024,
    "distance": "cosine",
    "message": "Collection 'project-X' created successfully"
}
```

**Tool Annotations:**
- readOnlyHint: False
- destructiveHint: False
- idempotentHint: True (creating same collection twice is safe)
- openWorldHint: True

**Error Handling:**
- Collection already exists → return success (idempotent)
- Invalid collection name → return error with guidance
- Invalid dimension → return error with valid ranges
- Qdrant connection error → return error with troubleshooting

---

## Implementation Plan

### Step 1: Add Tool to Reference MCP Server
**File:** `/home/hungson175/dev/deploy-memory-tools/src/qdrant_memory_mcp/__main__.py`

Add after line 679 (after list_collections):

```python
@mcp.tool(
    name="create_collection",
    annotations={
        "title": "Create Collection",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
def create_collection(
    collection_name: str,
    dimension: Optional[int] = None,
    distance: str = "cosine"
) -> str:
    """
    Create a new memory collection dynamically.
    
    Args:
        collection_name: Name of the collection to create (e.g., "proj-my-project", "custom-role")
        dimension: Vector dimension (default: EMBEDDING_DIMENSION from config)
        distance: Distance metric - "cosine", "euclid", or "dot" (default: "cosine")
    
    Returns:
        JSON string with creation confirmation
    """
    try:
        client = get_qdrant_client()
        dimension = dimension or EMBEDDING_DIMENSION
        
        # Validate distance metric
        distance_map = {
            "cosine": models.Distance.COSINE,
            "euclid": models.Distance.EUCLID,
            "dot": models.Distance.DOT
        }
        
        if distance not in distance_map:
            return json.dumps({
                "error": f"Invalid distance metric '{distance}'. Valid options: cosine, euclid, dot"
            })
        
        # Check if collection already exists (idempotent)
        try:
            client.get_collection(collection_name)
            return json.dumps({
                "collection_name": collection_name,
                "status": "success",
                "message": f"Collection '{collection_name}' already exists",
                "dimension": dimension,
                "distance": distance
            })
        except Exception:
            # Collection doesn't exist, create it
            pass
        
        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=dimension,
                distance=distance_map[distance]
            )
        )
        
        logger.info(f"Created collection '{collection_name}' (dimension={dimension}, distance={distance})")
        
        return json.dumps({
            "collection_name": collection_name,
            "status": "success",
            "message": f"Collection '{collection_name}' created successfully",
            "dimension": dimension,
            "distance": distance
        })
        
    except Exception as e:
        logger.error(f"Create collection error: {str(e)}")
        return json.dumps({"error": str(e)})
```

### Step 2: Test Implementation
**Manual Test:**
```bash
# Test via Claude Code MCP tools
create_collection(collection_name="proj-test", dimension=1024, distance="cosine")
```

**Expected Output:**
```json
{
  "collection_name": "proj-test",
  "status": "success",
  "message": "Collection 'proj-test' created successfully",
  "dimension": 1024,
  "distance": "cosine"
}
```

### Step 3: Verify with list_collections
```bash
list_collections()
# Should show "proj-test" in the list
```

---

## Testing Strategy

### Unit Tests
- Test collection creation (new collection)
- Test idempotency (creating same collection twice)
- Test invalid distance metric
- Test invalid collection name
- Test Qdrant connection error

### Integration Tests
- Create collection → store memory → search → fetch
- Create custom role collection
- Create project-specific collection

---

## Acceptance Criteria

- [ ] create_collection tool added to MCP server
- [ ] Tool creates collection with specified dimension and distance
- [ ] Idempotent (safe to call multiple times)
- [ ] Proper error handling
- [ ] Tool annotations correct
- [ ] Manual test passes
- [ ] Integration test: create → store → search workflow
- [ ] Documentation updated

---

## Estimated Time

**Total:** ~1 hour
- Add tool implementation: 20 min
- Manual testing: 15 min
- Integration testing: 15 min
- Documentation: 10 min

---

## Risk Assessment

**Low Risk** - Adding one tool to existing working system:
- Doesn't modify existing tools
- Idempotent design prevents issues
- Reference implementation stable
- Can test in isolation

---

**Next Step:** Await Boss approval to proceed with implementation.
