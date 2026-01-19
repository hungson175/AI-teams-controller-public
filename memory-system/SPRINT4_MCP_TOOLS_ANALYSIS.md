# Sprint 4: Complete MCP Server - Tool Documentation

**Goal:** Build complete MCP server with ALL 8 tools

---

## Current 'memory' MCP Server Tools (from testing)

### Tool 1: search_memory

**Input:**
- `query` (str): Search query text
- `roles` (List[str], optional): List of roles to search (e.g., ["backend", "universal"])
- `limit` (int, optional): Maximum results (default: 20)

**Output (JSON):**
```json
{
  "results": [
    {
      "doc_id": "uuid-string",
      "title": "...",
      "description": "...",
      "similarity": 0.664,
      "memory_type": "episodic|semantic|procedural",
      "tags": ["tag1", "tag2"],
      "role": "backend",
      "created_at": "ISO timestamp"
    }
  ],
  "total": 1,
  "message": "Found X memory previews. Use get_memory(doc_id) to retrieve full content."
}
```

**Behavior:** Two-stage retrieval - returns previews only (no full content)

---

### Tool 2: get_memory

**Input:**
- `doc_id` (str): UUID document ID
- `roles` (List[str], optional): Roles to search in

**Output (JSON):**
```json
{
  "doc_id": "uuid-string",
  "document": "**Title:**...**Description:**...**Content:**...**Tags:**...",
  "metadata": {
    "memory_type": "episodic",
    "role": "backend",
    "tags": ["tag1", "tag2"],
    "title": "...",
    "confidence": 0.95,
    "frequency": 1,
    "created_at": "ISO timestamp",
    "last_synced": "ISO timestamp",
    "description": "..."
  }
}
```

**Behavior:** Returns full document with complete metadata

---

### Tool 3: batch_get_memories

**Input:**
- `doc_ids` (List[str]): List of UUID document IDs
- `roles` (List[str], optional): Roles to search in

**Output (JSON):**
```json
{
  "memories": [
    {
      "doc_id": "uuid-string",
      "document": "...",
      "metadata": {...}
    }
  ],
  "retrieved": 1,
  "requested": 1
}
```

**Behavior:** Efficiently retrieves multiple documents

---

### Tool 4: store_memory

**Input:**
- `document` (str): Full formatted memory text
- `metadata` (dict): Metadata including memory_type, role, tags, title, description, frequency

**Output (JSON):**
```json
{
  "doc_id": "new-uuid",
  "status": "success",
  "collection": "backend",
  "message": "Memory stored successfully"
}
```

---

### Tool 5: update_memory

**Input:**
- `doc_id` (str): UUID to update
- `document` (str): New formatted memory text
- `metadata` (dict): Updated metadata

**Output (JSON):**
```json
{
  "doc_id": "uuid",
  "status": "success",
  "collection": "backend",
  "message": "Memory updated successfully"
}
```

---

### Tool 6: delete_memory

**Input:**
- `doc_id` (str): UUID to delete
- `roles` (List[str], optional): Roles to search in

**Output (JSON):**
```json
{
  "doc_id": "uuid",
  "status": "success",
  "remaining_memories": 123,
  "collection": "backend",
  "message": "Memory deleted successfully"
}
```

---

### Tool 7: list_collections

**Input:** (none)

**Output (JSON):**
```json
{
  "collections": [
    {
      "name": "backend",
      "count": 45,
      "level": "global",
      "role": "backend"
    }
  ],
  "total_collections": 15
}
```

---

### Tool 8: create_collection (NEW - to be implemented)

**Input:**
- `collection_name` (str): Collection name (e.g., "product-owner")

**Defaults:**
- dimension: 1024
- distance: COSINE

**Output (JSON):**
```json
{
  "collection_name": "product-owner",
  "status": "created",
  "dimension": 1024,
  "distance": "cosine",
  "message": "Collection 'product-owner' created successfully"
}
```

**Behavior:** Idempotent (safe if collection exists)

---

## Next Steps

1. ✅ Analyzed current MCP server tool APIs
2. ⏳ Read mcp-builder skill for implementation guidance
3. ⏳ Read memory_guide_draft_v7.md for design context
4. ⏳ Build complete MCP server with all 8 tools

---
