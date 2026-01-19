# Test Fixtures for Sprint 4 MCP Server

## Overview

This directory contains real memory data extracted from the current 'memory' MCP server for use in TDD (Test-Driven Development) for Sprint 4 MCP server implementation.

## Extraction Details

- **Date**: 2026-01-19
- **Source**: Current 'memory' MCP server (via mcp__memory__search_memory and mcp__memory__batch_get_memories)
- **Total Memories**: 29
- **Roles Covered**: backend (4), frontend (8), qa (2), devops (3), universal (8), scrum-master (3), universal-patterns (1)

## Directory Structure

```
tests/fixtures/
├── README.md                    # This file
└── memories/
    ├── all_memories.json        # Summary of all 29 memories (doc_ids, titles, tags, roles)
    ├── sample_full_memories.json # Full content for 5 representative memories
    └── [role]/                  # (future) Per-role JSON files
```

## Files

### 1. all_memories.json

Contains metadata for all 29 extracted memories:
- doc_id (UUID)
- role
- memory_type (episodic/semantic/procedural)
- title
- tags

Use this to generate test cases for search_memory (preview results).

### 2. sample_full_memories.json

Contains full memory documents (document + metadata) for 5 representative memories covering different roles and memory types.

Use this to generate test cases for:
- get_memory (single document retrieval)
- batch_get_memories (multiple document retrieval)
- store_memory (validate structure)
- update_memory (validate update operations)

## Memory Structure

### Preview Format (search_memory output)
```json
{
  "doc_id": "uuid-string",
  "title": "short title",
  "description": "2-3 sentence description",
  "similarity": 0.734,
  "memory_type": "episodic|semantic|procedural",
  "tags": ["tag1", "tag2"],
  "role": "backend",
  "created_at": "ISO timestamp"
}
```

### Full Memory Format (get_memory/batch_get_memories output)
```json
{
  "doc_id": "uuid-string",
  "document": "**Title:**...**Description:**...**Content:**...**Tags:**...",
  "metadata": {
    "memory_type": "episodic|semantic|procedural",
    "role": "backend",
    "tags": ["tag1", "tag2"],
    "title": "short title",
    "confidence": "high|medium|low" or 0.0-1.0,
    "frequency": 1,
    "created_at": "ISO timestamp",
    "last_synced": "ISO timestamp",
    "description": "2-3 sentence description"
  }
}
```

## Usage in Tests

### Example: Test search_memory

```python
import json
from pathlib import Path

def test_search_memory_returns_previews():
    # Load test fixtures
    fixtures = json.loads(Path("tests/fixtures/memories/all_memories.json").read_text())

    # Use doc_ids and metadata to validate search results
    expected_titles = [m["title"] for m in fixtures["memories"] if m["role"] == "backend"]

    # Call your search_memory implementation
    result = search_memory(query="backend patterns", roles=["backend"], limit=10)

    # Assert structure matches
    assert "results" in result
    assert len(result["results"]) <= 10
    for item in result["results"]:
        assert "doc_id" in item
        assert "title" in item
        assert "description" in item
```

### Example: Test get_memory

```python
def test_get_memory_returns_full_document():
    # Load full memory samples
    samples = json.loads(Path("tests/fixtures/memories/sample_full_memories.json").read_text())

    backend_memory = samples["backend_example"]
    doc_id = backend_memory["doc_id"]

    # Call your get_memory implementation
    result = get_memory(doc_id=doc_id, roles=["backend"])

    # Assert structure
    assert "doc_id" in result
    assert "document" in result
    assert "metadata" in result
    assert "**Title:**" in result["document"]
```

## Coverage

The 29 memories provide coverage across:

**Memory Types**:
- Episodic: 7 memories (specific incidents)
- Semantic: 14 memories (patterns/principles)
- Procedural: 8 memories (workflows/processes)

**Roles**:
- backend: 4
- frontend: 8
- qa: 2
- devops: 3
- universal: 8
- scrum-master: 3
- universal-patterns: 1

**Tags** (sample):
- testing (15 memories)
- failure patterns (7 memories)
- TDD (5 memories)
- database (3 memories)
- deployment (3 memories)

This provides diverse test data for validating search, retrieval, and filtering operations.

## Notes

- All doc_ids are UUIDs (as used by current 'memory' MCP server)
- Sprint 4 implementation will need UUID ↔ int mapping for Sprint 2/3 compatibility
- Metadata structure matches current 'memory' MCP server format
- Document content is formatted markdown with **Title:**, **Description:**, **Content:**, **Tags:** sections
