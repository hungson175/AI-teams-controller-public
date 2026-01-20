---
name: memory-store
description: Store coding patterns into GLOBAL vector database (cross-project learning). Auto-invokes after difficult tasks with broadly-applicable lessons. Trigger with "--store" or when user expresses frustration (fuck, bitch, dog, bad words = strong signal to call memory-store).
---

<execution>
Use Task tool with `subagent_type: "memory-only"` to keep main context clean.

The memory-only agent has ZERO access to Read/Write/Edit/Glob/Bash - it can ONLY use MCP memory tools. This prevents file reading pollution by design.
</execution>

<selectivity>
**EXTREMELY SELECTIVE** - Most of the time: DOESN'T insert.

Safe: <1 insertion per task. 2-3 insertions almost NEVER happen.

Store when: Non-obvious bugs, hard-won failure lessons, universal patterns across projects, user frustration signals.

Skip when: Standard practices, project-specific config, routine fixes, vague insights.
</selectivity>

<workflow>
**Step 1: Format memory**
```markdown
**Title:** [Concise title]
**Preview:** [2-3 sentence summary - CRITICAL for search]

**Content:** [What happened, what was tried, what worked/failed, key lesson]

**Tags:** #role #topic #success|#failure
```

**Step 2: Extract metadata**
Parse the formatted text to extract:
- `title`: Plain text without markdown (from "**Title:**")
- `preview`: Plain text without markdown (from "**Preview:**")

**Step 3: Detect role for storage**
Determine which role collection to store in based on task context. Use role_mapping below. Default to "OTHER" if unclear.

**Step 4: Search for duplicates**
Use `search_memory` with full formatted text as query, `roles=["detected_role", "OTHER"]`, `limit=10`.

Note: The `roles` parameter tells MCP which collections to search.

**Step 4.5: Review and fetch specific memories**
After search returns previews:
1. LLM reads the preview texts (10 results)
2. Select 3-4 that might match or conflict with new memory
3. FETCH those specific ones using `batch_get_memories(doc_ids, roles=["detected_role", "OTHER"])`
4. Read fetched full content to decide: duplicate? merge? update?

**Important:** Don't rely on similarity score - rely on LLM review of actual content.

**Step 5: Decide action**
Based on fetched content review:
- Near-identical exists → MERGE (combine, delete old)
- Related exists → UPDATE (enhance existing)
- Pattern emerges from 2+ episodic → GENERALIZE to semantic
- Different topic → CREATE new

**Step 6: Store**
Use `store_memory(document, role, metadata)` with:
- `document`: Full formatted markdown text (Title + Preview + Content + Tags)
- `role`: Collection name (backend, frontend, scrum-master, qa, OTHER)
- `metadata`: 3-field dict extracted from document:
```json
{
  "title": "Plain text title (extracted from **Title:** line)",
  "preview": "2-3 sentence summary (extracted from **Preview:** line)",
  "content": "[Full formatted markdown document - same as document parameter]"
}
```

**API Clarification:**
- `document` = the full markdown text
- `role` = which collection to store in
- `metadata` = {title, preview, content} - 3 fields extracted from document
</workflow>

<role_mapping>
Available roles (maps to Qdrant collections):
- backend: API, endpoint, database, server, auth
- frontend: React, Vue, component, UI, CSS
- scrum-master: Agile, sprint, standup, retrospective, planning
- po: Product management, backlog, priorities, stakeholders
- qa: Testing, quality assurance, verification, validation
- OTHER: General patterns, cross-domain knowledge

Default to "OTHER" if unclear. Each role corresponds to a separate Qdrant collection.

Note: Can add new roles via MCP as needed.
</role_mapping>
