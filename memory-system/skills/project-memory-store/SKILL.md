---
name: project-memory-store
description: Store universal coding patterns into vector database. Auto-invokes after difficult tasks with broadly-applicable lessons. Trigger with "--store" or when user expresses frustration (strong learning signals).
---

<execution>
Use Task tool with `subagent_type: "memory-agent"` to keep main context clean.

The memory-agent has ZERO access to Read/Write/Edit/Glob/Bash - it can ONLY use MCP memory tools. This prevents file reading pollution by design.
</execution>

<selectivity>
Store 0-1 insights per task (rarely 2-3).

Store when: Non-obvious bugs, hard-won failure lessons, universal patterns across projects, user frustration signals.

Skip when: Standard practices, project-specific config, routine fixes, vague insights.
</selectivity>

<workflow>
**Step 1: Format memory**
```
**Title:** [Concise title]
**Description:** [2-3 sentence summary - CRITICAL for search]

**Content:** [What happened, what was tried, what worked/failed, key lesson]

**Tags:** #role #topic #success|#failure
```

**Step 2: Extract metadata**
Parse the formatted text to extract:
- `title`: Plain text without markdown (from "**Title:**")
- `description`: Plain text without markdown (from "**Description:**")
- `tags`: Array of tags (e.g., ["#backend", "#jwt", "#auth"])

**Step 3: Detect role for storage**
Determine which role collection to store in based on task context. Use role_mapping below. Default to "universal" if unclear.

**Step 4: Search for duplicates**
Use `search_memory` with full formatted text as query, `roles=["detected_role", "universal"]`, `limit=10`.

Note: The `roles` parameter tells MCP which collections to search. Always include "universal" to catch cross-domain patterns.

**Step 5: Decide action**
- Near-identical exists → MERGE (combine, delete old)
- Related exists → UPDATE (enhance existing)
- Pattern emerges from 2+ episodic → GENERALIZE to semantic
- Different topic → CREATE new

**Step 6: Store**
Use `store_memory` with:
- `document`: Full formatted text (Title + Description + Content + Tags)
- `metadata`:
```json
{
  "memory_type": "episodic|procedural|semantic",
  "role": "backend|frontend|devops|ai|...",
  "title": "Plain text title",
  "description": "2-3 line summary",
  "tags": ["#tag1", "#tag2"],
  "confidence": "high|medium|low",
  "frequency": 1
}
```
</workflow>

<role_mapping>
Available roles (maps to Qdrant collections):
- universal: General patterns applicable across domains
- backend: API, endpoint, database, server, auth
- frontend: React, Vue, component, UI, CSS
- devops: Deploy, Docker, Kubernetes, CI/CD
- ai: Model, training, embedding, LLM
- security: Vulnerability, encryption, JWT
- mobile: iOS, Android, Flutter, Swift
- pm: Project management, coordination, delegation, reporting
- scrum-master: Agile, sprint, standup, retrospective, planning
- qa: Testing, quality assurance, verification, validation
- quant: Trading, backtesting, portfolio, risk

Default to "universal" if unclear. Each role maps to a collection named "{role}-patterns" (e.g., "backend-patterns").
</role_mapping>

<frustration_signals>
User frustration = critical learning moment. When detected (profanity, "this is ridiculous", emotional language): Store as episodic with #failure #strong-signal tags.
</frustration_signals>
