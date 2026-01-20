# Sprint 4: MCP Server Implementation - DRAFT PLAN

**Status:** AWAITING BOSS APPROVAL - DO NOT IMPLEMENT YET

---

## Goal

Wrap Sprint 3 functions (search, fetch, batch_fetch) as MCP tools using FastMCP framework.

---

## Architecture Overview

### Server Structure
```
memory-system/
├── src/
│   ├── memory/
│   │   ├── __init__.py
│   │   └── search_engine.py  (Sprint 3 - existing)
│   └── mcp/
│       ├── __init__.py
│       └── memory_mcp.py      (Sprint 4 - NEW)
├── tests/
│   ├── memory/
│   │   └── test_search_engine.py  (Sprint 3 - existing)
│   └── mcp/
│       ├── __init__.py
│       └── test_memory_mcp.py     (Sprint 4 - NEW)
└── requirements.txt (update with mcp dependency)
```

### MCP Server Design

**Server Name:** `memory_mcp` (follows {service}_mcp pattern)

**Transport:** stdio (for local Claude Code integration)

**Tools to Implement (3):**
1. `memory_search` - Search for memories (preview-only)
2. `memory_fetch` - Fetch single full document
3. `memory_batch_fetch` - Fetch multiple full documents

---

## Tool Specifications

### Tool 1: memory_search

**Purpose:** Search for memories and return preview-only results (like Google search)

**Input Schema (Pydantic):**
```python
class MemorySearchInput(BaseModel):
    query: str = Field(..., description="Search query text", min_length=2, max_length=500)
    collection: str = Field(..., description="Qdrant collection name (role)", min_length=1, max_length=100)
    limit: int = Field(default=20, description="Maximum results to return", ge=1, le=100)
    response_format: ResponseFormat = Field(default="markdown", description="Output format")
```

**Output:**
- Markdown (default): Formatted list of previews with scores
- JSON: Structured array of preview objects

**Tool Annotations:**
- readOnlyHint: True
- destructiveHint: False
- idempotentHint: True
- openWorldHint: True (interacts with Qdrant/Voyage)

**Implementation:**
- Calls `search_engine.search()` from Sprint 3
- Adds response formatting (Markdown/JSON)
- Error handling with actionable messages

---

### Tool 2: memory_fetch

**Purpose:** Fetch full document content for a single memory

**Input Schema (Pydantic):**
```python
class MemoryFetchInput(BaseModel):
    doc_id: int = Field(..., description="Document ID to retrieve", ge=1)
    collection: str = Field(..., description="Qdrant collection name (role)", min_length=1, max_length=100)
    response_format: ResponseFormat = Field(default="markdown", description="Output format")
```

**Output:**
- Markdown (default): Formatted document with title, preview, content, tags
- JSON: Structured document object

**Tool Annotations:**
- readOnlyHint: True
- destructiveHint: False
- idempotentHint: True
- openWorldHint: True

**Implementation:**
- Calls `search_engine.fetch()` from Sprint 3
- Adds response formatting (Markdown/JSON)
- Error handling with actionable messages

---

### Tool 3: memory_batch_fetch

**Purpose:** Fetch multiple documents across collections efficiently

**Input Schema (Pydantic):**
```python
class DocRef(BaseModel):
    doc_id: int = Field(..., description="Document ID", ge=1)
    collection: str = Field(..., description="Collection name", min_length=1, max_length=100)

class MemoryBatchFetchInput(BaseModel):
    doc_refs: List[DocRef] = Field(..., description="List of (doc_id, collection) pairs", min_items=1, max_items=50)
    response_format: ResponseFormat = Field(default="markdown", description="Output format")
```

**Output:**
- Markdown (default): Formatted list of documents with metadata
- JSON: Structured array of document objects

**Tool Annotations:**
- readOnlyHint: True
- destructiveHint: False
- idempotentHint: False (order matters, results vary by input)
- openWorldHint: True

**Implementation:**
- Calls `search_engine.batch_fetch()` from Sprint 3
- Converts List[DocRef] to List[Tuple[int, str]] for backend
- Adds response formatting (Markdown/JSON)
- Error handling with actionable messages

---

## Implementation Details

### Dependencies

**Add to requirements.txt:**
```
mcp>=1.0.0
```

### Shared Utilities

```python
# Response format enum
class ResponseFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"

# Error handling
def _handle_error(e: Exception) -> str:
    if isinstance(e, ValueError):
        return f"Error: {str(e)}"
    return f"Error: Unexpected error occurred: {type(e).__name__}"

# Format helpers
def _format_search_results_markdown(results: List[Dict]) -> str:
    # Format previews as markdown

def _format_search_results_json(results: List[Dict]) -> str:
    # Return JSON string

def _format_document_markdown(doc: Dict) -> str:
    # Format single document as markdown

def _format_document_json(doc: Dict) -> str:
    # Return JSON string
```

### FastMCP Server Initialization

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("memory_mcp")

if __name__ == "__main__":
    mcp.run()  # stdio transport by default
```

---

## Testing Strategy (TDD)

### Test Structure

```
tests/mcp/test_memory_mcp.py
├── Test memory_search tool
│   ├── test_search_with_results_markdown
│   ├── test_search_with_results_json
│   ├── test_search_empty_results
│   ├── test_search_invalid_collection
│   └── test_search_input_validation
├── Test memory_fetch tool
│   ├── test_fetch_document_markdown
│   ├── test_fetch_document_json
│   ├── test_fetch_not_found
│   └── test_fetch_input_validation
└── Test memory_batch_fetch tool
    ├── test_batch_fetch_multiple_collections_markdown
    ├── test_batch_fetch_multiple_collections_json
    ├── test_batch_fetch_partial_results
    └── test_batch_fetch_input_validation
```

**Total Test Cases:** ~13 tests

**Testing Approach:**
1. Mock Sprint 3 functions (search, fetch, batch_fetch)
2. Test input validation (Pydantic)
3. Test response formatting (Markdown/JSON)
4. Test error handling
5. Test tool annotations

**Coverage Target:** 80%+ (following Sprint 3 standard)

---

## Implementation Steps

### Phase 1: TDD - Write Tests First (Est: 30-45 min)
1. Create tests/mcp/__init__.py
2. Create tests/mcp/test_memory_mcp.py
3. Write all 13 test cases (AC-driven)
4. Run tests (expect failures)

### Phase 2: Implementation (Est: 45-60 min)
1. Create src/mcp/__init__.py
2. Create src/mcp/memory_mcp.py
3. Implement FastMCP server initialization
4. Implement 3 tools with Pydantic models
5. Implement shared utilities (formatting, error handling)
6. Add comprehensive docstrings

### Phase 3: Testing & Coverage (Est: 15-20 min)
1. Run tests: `pytest tests/mcp/test_memory_mcp.py -v`
2. Run coverage: `pytest --cov=src/mcp --cov-report=term-missing --cov-report=html:tests/results/sprint4/htmlcov --cov-report=json:tests/results/sprint4/coverage.json`
3. Verify 80%+ coverage
4. Create tests/results/sprint4/COVERAGE_REPORT.txt

### Phase 4: Manual Testing (Est: 10-15 min)
1. Test server startup: `python src/mcp/memory_mcp.py --help`
2. (Optional) Test with MCP Inspector if available
3. Verify all imports resolve

---

## Acceptance Criteria

- [ ] All 13 tests passing (100%)
- [ ] 80%+ code coverage on src/mcp/memory_mcp.py
- [ ] Server runs without errors: `python src/mcp/memory_mcp.py --help`
- [ ] All 3 tools registered with proper names
- [ ] Pydantic input validation working
- [ ] Response formatting (Markdown/JSON) implemented
- [ ] Error handling with actionable messages
- [ ] Tool annotations set correctly
- [ ] Comprehensive docstrings with type information
- [ ] Code follows DRY principle (no duplication)
- [ ] Coverage evidence committed

---

## Integration Notes

### How Claude Code Will Use This

**In claude.json (MCP server configuration):**
```json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": [
        "/path/to/memory-system/src/mcp/memory_mcp.py"
      ],
      "transport": "stdio"
    }
  }
}
```

**Claude Code will see 3 tools:**
- `memory_search` - For searching memories
- `memory_fetch` - For retrieving full content
- `memory_batch_fetch` - For bulk retrieval

---

## Open Questions for Boss Review

1. **Response Format Default:** Should default be Markdown or JSON? (Recommendation: Markdown for human-readable)
2. **Collection Validation:** Should we validate collection names against known roles, or allow any string? (Recommendation: Allow any string, let Qdrant handle validation)
3. **Batch Size Limit:** max_items=50 for batch_fetch seems reasonable? (Recommendation: Yes, prevents memory issues)
4. **Error Messages:** How detailed should error messages be? (Recommendation: Specific but not exposing internals)

---

## Definition of Done

- [ ] Boss approval of this plan
- [ ] All test cases passing (13/13)
- [ ] 80%+ code coverage with evidence
- [ ] Server runs successfully
- [ ] All tools registered and functional
- [ ] Code committed to git with clear messages
- [ ] Integration tested with Claude Code (if possible)

---

**Next Step:** PO forwards this plan to Boss for approval. After approval, DEV implements with TDD approach.
