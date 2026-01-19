# Sprint 4: Complete MCP Server Implementation Plan

**Status:** DRAFT - Awaiting Boss Approval  
**Date:** 2026-01-19

---

## Overview

**Goal:** Build complete MCP server with 8 tools using FastMCP framework

**Approach:** 
- TDD (tests first for all tools)
- FastMCP with Pydantic validation
- Integrate with Sprint 3 search_engine.py where applicable
- Follow v7 spec design principles

**Estimated Total Time:** 4-5 hours

---

## Architecture

### MCP Server Structure

```
memory-system/
├── src/
│   ├── memory/
│   │   ├── __init__.py
│   │   └── search_engine.py          (Sprint 3 - existing)
│   └── mcp_server/
│       ├── __init__.py
│       ├── server.py                  (FastMCP server - NEW)
│       ├── models.py                  (Pydantic schemas - NEW)
│       └── tools/
│           ├── __init__.py
│           ├── search_tools.py        (search, get, batch_get - NEW)
│           ├── mutation_tools.py      (store, update, delete - NEW)
│           └── admin_tools.py         (list_collections, create_collection - NEW)
├── tests/
│   ├── memory/
│   │   └── test_search_engine.py      (Sprint 3 - existing)
│   └── mcp_server/
│       ├── __init__.py
│       ├── test_search_tools.py       (NEW)
│       ├── test_mutation_tools.py     (NEW)
│       └── test_admin_tools.py        (NEW)
└── requirements.txt                    (add mcp dependency)
```

### FastMCP Server Initialization

**File:** `src/mcp_server/server.py`

```python
from mcp.server.fastmcp import FastMCP
from .tools import search_tools, mutation_tools, admin_tools

# Initialize FastMCP server
mcp = FastMCP("memory")

# Register all tools (imported from tool modules)
# Tools auto-register via decorators in tool modules

if __name__ == "__main__":
    mcp.run()  # stdio transport
```

---

## Tool Implementations

### Tool 1: search_memory

**Purpose:** Two-stage retrieval - semantic search returning previews only

**Pydantic Schema:**
```python
class SearchMemoryInput(BaseModel):
    query: str = Field(..., description="Search query text", min_length=2, max_length=500)
    roles: Optional[List[str]] = Field(default=None, description="List of roles to search (e.g., ['backend', 'universal'])")
    limit: int = Field(default=20, description="Maximum results to return", ge=1, le=100)
```

**Implementation Strategy:**
- Use Sprint 3 `search_engine.search()` for backend logic
- Convert Sprint 3 results to match current 'memory' MCP server format
- Handle UUID vs int doc_id mismatch (generate UUIDs if needed)
- Format output as JSON string

**Tool Annotations:**
- readOnlyHint: True
- destructiveHint: False
- idempotentHint: True
- openWorldHint: True

**Test Cases (5):**
1. Search with results - returns previews only
2. Search empty results
3. Search with multiple roles
4. Search respects limit parameter
5. Search with invalid role (graceful handling)

---

### Tool 2: get_memory

**Purpose:** Fetch single full document by UUID

**Pydantic Schema:**
```python
class GetMemoryInput(BaseModel):
    doc_id: str = Field(..., description="Document UUID to retrieve")
    roles: Optional[List[str]] = Field(default=None, description="Roles to search in (optional)")
```

**Implementation Strategy:**
- Use Sprint 3 `search_engine.fetch()` for retrieval
- Handle UUID → int conversion for Sprint 3 backend
- Return full document with metadata
- Format output as JSON string

**Tool Annotations:**
- readOnlyHint: True
- destructiveHint: False
- idempotentHint: True
- openWorldHint: True

**Test Cases (4):**
1. Fetch existing document - returns full content
2. Fetch non-existent document - error message
3. Fetch with roles specified
4. Fetch with UUID validation

---

### Tool 3: batch_get_memories

**Purpose:** Efficiently fetch multiple documents

**Pydantic Schema:**
```python
class BatchGetMemoriesInput(BaseModel):
    doc_ids: List[str] = Field(..., description="List of document UUIDs", min_items=1, max_items=50)
    roles: Optional[List[str]] = Field(default=None, description="Roles to search in (optional)")
```

**Implementation Strategy:**
- Use Sprint 3 `search_engine.batch_fetch()` for retrieval
- Convert UUID list → int list for Sprint 3 backend
- Deduplicate results
- Format output as JSON string

**Tool Annotations:**
- readOnlyHint: True
- destructiveHint: False
- idempotentHint: True
- openWorldHint: True

**Test Cases (4):**
1. Batch fetch multiple documents
2. Batch fetch with partial results (some missing)
3. Batch fetch preserves order
4. Batch fetch with empty list

---

### Tool 4: store_memory

**Purpose:** Store new memory with auto-generated UUID

**Pydantic Schema:**
```python
class StoreMemoryInput(BaseModel):
    document: str = Field(..., description="Full formatted memory text", min_length=10)
    metadata: Dict[str, Any] = Field(..., description="Metadata including memory_type, role, tags, title, description")
```

**Implementation Strategy:**
- Generate UUID for new document
- Validate metadata fields (memory_type, role, tags required)
- Create embedding using Voyage API
- Store in Qdrant collection
- Return UUID and status

**Tool Annotations:**
- readOnlyHint: False
- destructiveHint: False
- idempotentHint: False
- openWorldHint: True

**Test Cases (5):**
1. Store new memory - returns UUID
2. Store with minimal metadata
3. Store with full metadata
4. Store with invalid role - error
5. Store with missing required fields - validation error

---

### Tool 5: update_memory

**Purpose:** Update existing memory (regenerates embedding)

**Pydantic Schema:**
```python
class UpdateMemoryInput(BaseModel):
    doc_id: str = Field(..., description="Document UUID to update")
    document: str = Field(..., description="New formatted memory text", min_length=10)
    metadata: Dict[str, Any] = Field(..., description="Updated metadata")
```

**Implementation Strategy:**
- Validate UUID exists
- Regenerate embedding
- Update Qdrant document
- Update timestamps (last_updated, last_synced)
- Return status

**Tool Annotations:**
- readOnlyHint: False
- destructiveHint: False
- idempotentHint: True
- openWorldHint: True

**Test Cases (4):**
1. Update existing document
2. Update non-existent document - error
3. Update with new embedding regenerated
4. Update timestamps correctly

---

### Tool 6: delete_memory

**Purpose:** Delete memory by UUID

**Pydantic Schema:**
```python
class DeleteMemoryInput(BaseModel):
    doc_id: str = Field(..., description="Document UUID to delete")
    roles: Optional[List[str]] = Field(default=None, description="Roles to search in (optional)")
```

**Implementation Strategy:**
- Validate UUID exists
- Delete from Qdrant
- Return remaining count
- Handle not found gracefully

**Tool Annotations:**
- readOnlyHint: False
- destructiveHint: True
- idempotentHint: True
- openWorldHint: True

**Test Cases (4):**
1. Delete existing document
2. Delete non-existent document - error
3. Delete returns remaining count
4. Delete idempotent (second delete is safe)

---

### Tool 7: list_collections

**Purpose:** List all collections with metadata

**Pydantic Schema:**
```python
# No input schema - tool takes no parameters
```

**Implementation Strategy:**
- Query Qdrant for all collections
- Get counts for each collection
- Classify as global vs project
- Format output as JSON string

**Tool Annotations:**
- readOnlyHint: True
- destructiveHint: False
- idempotentHint: True
- openWorldHint: True

**Test Cases (3):**
1. List all collections
2. List returns accurate counts
3. List classifies global vs project correctly

---

### Tool 8: create_collection (NEW)

**Purpose:** Dynamically create new collection

**Pydantic Schema:**
```python
class CreateCollectionInput(BaseModel):
    collection_name: str = Field(..., description="Collection name (e.g., 'product-owner', 'devops')", min_length=1, max_length=100)
```

**Defaults (hardcoded):**
- dimension: 1024 (Voyage AI)
- distance: COSINE

**Implementation Strategy:**
- Validate collection name (alphanumeric + hyphens)
- Check if collection exists (idempotent)
- Create collection with defaults
- Return status and config

**Tool Annotations:**
- readOnlyHint: False
- destructiveHint: False
- idempotentHint: True (safe to call multiple times)
- openWorldHint: True

**Test Cases (5):**
1. Create new collection - success
2. Create existing collection - returns "exists" status
3. Create with invalid name - validation error
4. Verify dimension=1024 default
5. Verify distance=COSINE default

---

## Integration with Sprint 3

### UUID vs Integer ID Mapping

**Challenge:** 
- Current 'memory' MCP server uses UUID strings
- Sprint 3 uses integers
- Sprint 2 Qdrant data uses integers

**Solution:**
```python
# Maintain bi-directional mapping
_uuid_to_int: Dict[str, int] = {}
_int_to_uuid: Dict[int, str] = {}

def _get_or_create_uuid(doc_id: int) -> str:
    """Convert int doc_id to UUID, creating if needed"""
    if doc_id not in _int_to_uuid:
        new_uuid = str(uuid4())
        _int_to_uuid[doc_id] = new_uuid
        _uuid_to_int[new_uuid] = doc_id
    return _int_to_uuid[doc_id]

def _uuid_to_int_id(uuid_str: str) -> int:
    """Convert UUID to int doc_id"""
    return _uuid_to_int.get(uuid_str, -1)
```

### Embedding Generation

**Use existing Voyage AI setup from Sprint 1:**
```python
import voyageai
from dotenv import load_dotenv

voyage_client = voyageai.Client(api_key=os.getenv('VOYAGE_API_KEY'))

def _get_embedding(text: str) -> List[float]:
    """Generate embedding using Voyage API"""
    result = voyage_client.embed(
        texts=[text],
        model="voyage-4-lite"
    )
    return result.embeddings[0]
```

### Qdrant Client

**Reuse Sprint 3 client initialization:**
```python
from qdrant_client import QdrantClient

_qdrant_client = None

def _get_qdrant_client() -> QdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        url = os.getenv('QDRANT_URL', 'http://localhost:16333')
        _qdrant_client = QdrantClient(url=url)
    return _qdrant_client
```

---

## Testing Strategy (TDD)

### Phase 1: Write Tests First
**Estimated time:** 2 hours

1. **test_search_tools.py** (12 tests)
   - search_memory: 5 tests
   - get_memory: 4 tests
   - batch_get_memories: 4 tests

2. **test_mutation_tools.py** (13 tests)
   - store_memory: 5 tests
   - update_memory: 4 tests
   - delete_memory: 4 tests

3. **test_admin_tools.py** (8 tests)
   - list_collections: 3 tests
   - create_collection: 5 tests

**Total Test Cases:** 33 tests

**Testing Approach:**
- Mock Qdrant client
- Mock Voyage API
- Mock UUID generation (deterministic for tests)
- Test input validation (Pydantic)
- Test error handling
- Test output format (JSON)

### Phase 2: Implementation
**Estimated time:** 2 hours

1. Create Pydantic models (30 min)
2. Implement search tools (30 min)
3. Implement mutation tools (40 min)
4. Implement admin tools (20 min)

### Phase 3: Integration Testing
**Estimated time:** 30 min

1. Test full workflow: create_collection → store → search → fetch
2. Test UUID ↔ int mapping
3. Test with real Qdrant (port 16333)
4. Verify MCP server startup

### Phase 4: Coverage & Documentation
**Estimated time:** 30 min

1. Run coverage: target 80%+
2. Generate coverage report
3. Update documentation
4. Commit with evidence

---

## Dependencies

**Add to requirements.txt:**
```
mcp>=1.0.0
pydantic>=2.0.0
```

**Already have:**
- qdrant-client
- voyageai
- python-dotenv

---

## Acceptance Criteria

### Functional Requirements
- [ ] All 8 tools implemented with FastMCP decorators
- [ ] All tools have Pydantic input validation
- [ ] All tools have proper annotations
- [ ] All tools return JSON-formatted strings
- [ ] create_collection uses collection_name only (defaults: dim=1024, distance=COSINE)

### Testing Requirements
- [ ] 33 test cases written (TDD approach)
- [ ] All tests passing (33/33)
- [ ] 80%+ code coverage on src/mcp_server/
- [ ] Coverage evidence committed

### Integration Requirements
- [ ] Sprint 3 functions integrated correctly
- [ ] UUID ↔ int mapping working
- [ ] Qdrant client reused from Sprint 3
- [ ] Voyage API integrated

### MCP Server Requirements
- [ ] Server runs: `python src/mcp_server/server.py --help`
- [ ] All 8 tools registered
- [ ] Tools callable via MCP protocol
- [ ] Error handling graceful

---

## Implementation Order

### Day 1 (3-4 hours)

**Morning:**
1. Create directory structure (10 min)
2. Write Pydantic models (30 min)
3. Write all test files (TDD) (2 hours)
4. Run tests (expect failures) (10 min)

**Afternoon:**
5. Implement admin tools (20 min)
6. Implement search tools (30 min)
7. Implement mutation tools (40 min)
8. Run tests, fix issues (30 min)

### Day 1 Evening (1 hour)
9. Integration testing (30 min)
10. Coverage report (15 min)
11. Documentation (15 min)
12. Commit with evidence

---

## Risk Assessment

### Low Risk
- FastMCP framework well-documented
- Sprint 3 functions already working
- Clear API contracts from current 'memory' server

### Medium Risk
- UUID ↔ int mapping adds complexity
- 33 tests is significant scope
- Metadata structure differences between servers

### Mitigation
- Test UUID mapping thoroughly
- Break into smaller commits
- Reference current 'memory' server behavior closely

---

## Open Questions for Boss

1. **UUID Mapping:** Should we persist UUID ↔ int mapping to disk, or keep in-memory?
   - In-memory: Simple, but UUIDs change on server restart
   - Persisted: Complex, but stable UUIDs

2. **Metadata Structure:** Current 'memory' server has complex metadata (memory_type, confidence, frequency). Should Sprint 4 match exactly or simplify?
   - Match exactly: Compatible with current server
   - Simplify: Follow Sprint 2 design (title, preview, content only)

3. **Sprint 3 Integration:** Should we refactor Sprint 3 to use UUIDs, or keep adapter layer?
   - Refactor: Clean, but breaks Sprint 3 API
   - Adapter: Works, but adds complexity

4. **Testing Priority:** 33 tests is ambitious. Should we prioritize specific tools?
   - All tools equally: Full coverage
   - Focus on mutation tools: Higher risk

---

## Definition of Done

- [ ] Boss approves this plan
- [ ] All 8 tools implemented
- [ ] 33 test cases passing
- [ ] 80%+ coverage with evidence
- [ ] MCP server runs successfully
- [ ] Integration tested with real Qdrant
- [ ] Documentation updated
- [ ] Code committed with clear messages

---

**Next Step:** PO forwards this plan to Boss for approval. DEV will NOT implement until Boss approves.

---

**Prepared by:** DEV  
**Reviewed by:** PO (pending)  
**Approved by:** Boss (pending)
