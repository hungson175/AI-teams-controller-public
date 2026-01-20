# Sprint 3: Mini Search Engine - Technical Specification

## Goal
Build 3 reusable functions for two-stage memory retrieval (v7 spec line 266-280)

## Acceptance Criteria

### AC1: search() - Preview-Only Search
**Function**: `search(query: str, collection: str, limit: int = 20) -> List[Dict]`

**Input:**
- query: Search text (e.g., "rate limiting patterns")
- collection: Qdrant collection name (e.g., "backend")
- limit: Max results to return (default: 20)

**Output:** List of preview objects with:
```python
{
    "id": int,          # Document ID
    "title": str,       # Memory title
    "preview": str,     # 2-3 sentence description
    "score": float      # Similarity score (0-1)
}
```

**Behavior:**
- Generate embedding from query using Voyage API (voyage-4-lite)
- Search in specified Qdrant collection using query_points()
- Return ONLY id, title, preview, score (NOT full content)
- Sort by similarity score (highest first)
- Return empty list if collection not found

**Test Cases:**
1. Search returns list of preview objects (no content field)
2. Results sorted by similarity score
3. Respects limit parameter
4. Returns empty list for non-existent collection

---

### AC2: fetch() - Single Document Retrieval
**Function**: `fetch(doc_id: int, collection: str) -> Dict`

**Input:**
- doc_id: Document ID to retrieve
- collection: Qdrant collection name

**Output:** Full document object:
```python
{
    "id": int,
    "title": str,
    "preview": str,
    "content": str      # Full formatted content with tags
}
```

**Behavior:**
- Retrieve single document from Qdrant by ID
- Return full payload including content field
- Raise ValueError if doc_id not found
- Raise ValueError if collection not found

**Test Cases:**
1. Fetch returns full document with content field
2. Raises ValueError for non-existent doc_id
3. Raises ValueError for non-existent collection

---

### AC3: batch_fetch() - Multiple Document Retrieval Across Collections
**Function**: `batch_fetch(doc_refs: List[Tuple[int, str]]) -> List[Dict]`

**Input:**
- doc_refs: List of (doc_id, collection) tuples
  - Example: [(1, "backend"), (2, "qa"), (3, "backend")]
  - Allows fetching from multiple collections in one call

**Output:** List of full document objects with collection info:
```python
{
    "id": int,
    "collection": str,  # Which collection it came from
    "title": str,
    "preview": str,
    "content": str
}
```

**Behavior:**
- Group requests by collection for efficiency
- Retrieve documents across multiple collections
- Return list of full documents with content
- Skip doc_refs that don't exist (no error)
- Preserve order of input doc_refs
- Handle empty list gracefully

**Test Cases:**
1. Batch fetch returns documents from multiple collections
2. Skips non-existent doc_refs without error
3. Preserves input order
4. Groups requests by collection (performance optimization)
5. Handles empty doc_refs list

---

## Implementation Notes

### Module Structure
```
src/
  memory/
    search_engine.py     # Main module with 3 functions
    __init__.py

tests/
  memory/
    test_search_engine.py  # TDD tests
    __init__.py
```

### Dependencies
- qdrant-client (query_points, retrieve)
- voyageai (embed)
- python-dotenv (environment variables)

### API Compatibility
- Use `query_points()` NOT `search()` in qdrant-client
- Response access via `.points` attribute
- Parameter: `query=` NOT `query_vector=`

### Testing Strategy
**Tier 1:** Mock tests (no external dependencies)
**Tier 2:** Integration tests (real Qdrant + Voyage)
**Tier 3:** End-to-end validation

---

## Definition of Done
- [ ] All 12 test cases passing
- [ ] Module with clean API and docstrings
- [ ] Works with current Qdrant setup (port 16333)
- [ ] Code in src/memory/search_engine.py
- [ ] Committed to git with tests
