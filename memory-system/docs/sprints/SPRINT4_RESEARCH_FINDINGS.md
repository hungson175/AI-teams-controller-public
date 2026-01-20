# Sprint 4: Research Findings - FULL MCP Server Design

**Date:** 2026-01-19  
**Status:** Research Complete - Awaiting Boss Review

---

## Executive Summary

Sprint 4 is MUCH LARGER than initially planned. The full MCP server requires **7 tools** (not 3), collection management, multi-provider embedding support, and proper metadata handling.

---

## Current 'memory' MCP Server Analysis

### Tools Discovered (7 total)

#### Read-Only Tools (3)
1. **search_memory** - Semantic search returning previews
   - Input: query, roles (list), limit
   - Output: JSON with previews (title, description, similarity, metadata)
   - Two-stage retrieval: returns snippets, not full content

2. **get_memory** - Fetch single full document
   - Input: doc_id (UUID string), roles (optional)
   - Output: JSON with full document + metadata
   - Searches across multiple role collections if needed

3. **batch_get_memories** - Fetch multiple documents efficiently
   - Input: doc_ids (list of UUID strings), roles (optional)
   - Output: JSON with array of full documents
   - Deduplicates across collections

#### Write Tools (3)
4. **store_memory** - Store new memory
   - Input: document (formatted string), metadata (dict)
   - Generates UUID for new doc_id
   - Creates embedding and stores in appropriate collection
   - Returns: doc_id, status, collection

5. **update_memory** - Update existing memory
   - Input: doc_id, document, metadata
   - Regenerates embedding (important!)
   - Timestamps: last_updated, last_synced

6. **delete_memory** - Delete memory by ID
   - Input: doc_id, roles (optional)
   - Searches across collections to find and delete
   - Returns remaining count

#### Utility Tools (1)
7. **list_collections** - List all collections with metadata
   - No input
   - Returns: collection names, counts, level (global/project), role mapping

---

## Key Design Elements (Reference Implementation)

### 1. Role-Based Collections
```python
ROLE_COLLECTIONS = {
    "universal": "universal-patterns",
    "backend": "backend-patterns",
    "frontend": "frontend-patterns",
    "quant": "quant-patterns",
    "devops": "devops-patterns",
    "ml": "ml-patterns",
    "security": "security-patterns",
    "mobile": "mobile-patterns",
    "ai": "ai-patterns",
    "scrum-master": "scrum-master-patterns",
}
```
- Tools use "roles" parameter (e.g., ["backend", "universal"])
- Server maps role → collection name
- Auto-creates collections on startup

### 2. Metadata Schema
```python
{
    "document": "full formatted text",  # Gets embedded
    "title": "short title",
    "description": "2-3 sentence preview",
    "memory_type": "episodic|semantic|procedural",
    "role": "backend",
    "tags": ["#tag1", "#tag2"],
    "frequency": 1,
    "confidence": "high|medium|low",
    "created_at": "ISO timestamp",
    "last_updated": "ISO timestamp",
    "last_synced": "ISO timestamp"
}
```

### 3. Multiple Embedding Providers
- OpenAI: text-embedding-3-small (default)
- Voyage: voyage-3-large (Anthropic's recommended, +27% accuracy)
- Nomic: nomic-embed-text-v2-moe (open-source)
- Configurable via EMBEDDING_PROVIDER env var

### 4. UUID Document IDs
- Use UUID strings, NOT integers
- Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
- Sprint 3 uses integers - MISMATCH!

### 5. Two-Stage Retrieval (v7 spec)
- Stage 1: search_memory returns previews (snippets)
- Stage 2: get_memory/batch_get_memories fetch full content
- LLM decides relevance from previews
- More efficient: consider 50 items, load only 3-5

### 6. Collection Auto-Creation
```python
def _init_collections(client: QdrantClient):
    """Initialize all role-based collections if they don't exist"""
    for role, collection_name in ROLE_COLLECTIONS.items():
        try:
            client.get_collection(collection_name)
        except Exception:
            client.create_collection(...)
```

### 7. Embedding Cache
- In-memory cache: `_embedding_cache: Dict[str, List[float]]`
- Avoids redundant API calls
- Cleared on server restart

### 8. Logging to stderr
```python
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr  # CRITICAL for stdio transport!
)
```
- stdout is reserved for MCP protocol
- stderr for all logging

### 9. FastMCP Patterns
```python
@mcp.tool(
    name="tool_name",
    annotations={
        "title": "Human-Readable Title",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
def tool_function(param1: str, param2: Optional[List[str]] = None) -> str:
    """Tool description."""
    # Implementation
    return json.dumps(result)
```

---

## Sprint 3 vs Full MCP Server: Gap Analysis

### What Sprint 3 Has ✅
- search() function - semantic search with Qdrant + Voyage
- fetch() function - single document retrieval
- batch_fetch() function - multiple document retrieval
- Test coverage: 82%

### What Sprint 3 is MISSING ❌

#### Missing Tools (4)
- store_memory - Can't add new memories
- update_memory - Can't modify existing memories
- delete_memory - Can't remove memories
- list_collections - Can't see what collections exist

#### Architectural Mismatches
1. **Doc IDs:** Sprint 3 uses `int`, should use `str` (UUID)
2. **Collection Access:** Sprint 3 uses `collection: str` directly, should use `roles: List[str]` with mapping
3. **Metadata:** Sprint 3 has minimal metadata (title, preview, content), missing memory_type, tags, frequency, confidence, timestamps
4. **Collection Management:** Sprint 3 doesn't create collections, reference auto-creates
5. **Embedding Provider:** Sprint 3 hardcoded to Voyage, reference supports 3 providers
6. **Embedding Cache:** Sprint 3 doesn't cache, reference does

#### Missing Infrastructure
- No role → collection mapping
- No collection auto-creation
- No embedding provider configuration
- No UUID generation
- No timestamp management
- No embedding cache

---

## What Sprint 4 SHOULD Include

### Phase 1: Refactor Sprint 3 (Breaking Changes)
1. Change doc_id from `int` to `str` (UUID)
2. Change `collection: str` to `roles: List[str]`
3. Add ROLE_COLLECTIONS mapping
4. Update all Sprint 3 tests

### Phase 2: Add Write Tools (3 new tools)
1. Implement store_memory
2. Implement update_memory
3. Implement delete_memory
4. Write tests for each (TDD)

### Phase 3: Add Utility Tools (1 new tool)
1. Implement list_collections
2. Write tests (TDD)

### Phase 4: Add Infrastructure
1. Collection auto-creation (_init_collections)
2. Embedding cache
3. Multi-provider support (OpenAI, Voyage, Nomic)
4. Proper logging (stderr)
5. Metadata schema validation

### Phase 5: MCP Integration
1. Wrap all 7 tools with FastMCP decorators
2. Add tool annotations
3. Add comprehensive docstrings
4. Test with MCP Inspector
5. Integration testing

### Phase 6: Testing & Coverage
- Target: 15-20 new test cases (in addition to existing 12)
- Coverage: 80%+ on all new code
- Integration tests for full workflows

---

## Estimated Scope

**Original Sprint 4 Plan:** ~2 hours (3 tools, wrapping only)

**Revised Sprint 4 Scope:** ~6-8 hours
- Phase 1: Refactor Sprint 3 (1 hour)
- Phase 2: Write tools (2 hours)
- Phase 3: Utility tools (30 min)
- Phase 4: Infrastructure (1.5 hours)
- Phase 5: MCP integration (1.5 hours)
- Phase 6: Testing (1.5 hours)

**Recommendation:** Split into Sprint 4A and Sprint 4B if needed.

---

## Open Questions for Boss

1. **Sprint Scope:** Should Sprint 4 include ALL 7 tools + infrastructure, or split into 4A (read-only) and 4B (write + utility)?

2. **Sprint 3 Refactoring:** Sprint 3 is already committed with int doc_ids. Should we:
   - Option A: Keep Sprint 3 as-is, build new MCP layer on top
   - Option B: Refactor Sprint 3 to match reference design (breaking changes)

3. **Embedding Provider:** Should Sprint 4 support all 3 providers (OpenAI, Voyage, Nomic) or just Voyage?

4. **Collection Naming:** Reference uses "{role}-patterns" (e.g., "backend-patterns"). Should we follow this exactly?

5. **Metadata Schema:** Should we implement the FULL metadata schema from reference, or a simplified version?

6. **Testing Priority:** Given larger scope, should we prioritize:
   - Option A: All tools working, lower test coverage (~60%)
   - Option B: Fewer tools, high test coverage (80%+)

---

## Recommendation

**Option 1 (Recommended):** Split into 2 sprints
- **Sprint 4A:** Read-only tools (3) + infrastructure + refactor Sprint 3
  - Refactor Sprint 3 to use UUIDs and roles
  - Add collection auto-creation
  - Add embedding cache and multi-provider support
  - Wrap 3 read-only tools as MCP
  - Est: 3-4 hours

- **Sprint 4B:** Write tools (3) + utility (1) + full integration
  - Implement store, update, delete
  - Implement list_collections
  - Full integration testing
  - Est: 3-4 hours

**Option 2:** Single large Sprint 4
- All 7 tools + infrastructure in one go
- Risk: rushed testing, lower quality
- Est: 6-8 hours

---

## Next Steps

Awaiting Boss decision on:
1. Sprint scope (4A/4B split vs single sprint)
2. Sprint 3 refactoring approach
3. Embedding provider support level
4. Metadata schema completeness
5. Testing priority

After Boss approval, DEV will create detailed implementation plan with acceptance criteria.

---

**Prepared by:** DEV  
**Reviewed by:** PO (pending)  
**Approved by:** Boss (pending)
