---
name: project-memory-recall
description: Retrieve universal coding patterns from vector database. Auto-invokes before complex tasks or when user says "--recall". Searches relevant role collections based on task context.
---

<execution>
Use Task tool with `subagent_type: "memory-agent"` to keep main context clean.

The memory-agent has ZERO access to Read/Write/Edit/Glob/Bash - it can ONLY use MCP memory tools. This prevents file reading pollution by design.
</execution>

<selectivity>
Search when: Non-obvious bugs, complex architectures, performance issues, unfamiliar domains, hard problems.

Skip when: Obvious tasks, basic file operations, standard workflows, problems solvable with basic knowledge.
</selectivity>

<workflow>
**Step 1: Build semantic query**
Construct 2-3 sentences capturing: What is the problem? What is the technical context? What outcome is desired?

Example: "Need to implement rate limiting for REST API to prevent abuse. Backend service in Node.js with Express. Want proven pattern that prevents thundering herd."

**Step 2: Detect relevant roles**
Determine which role collections to search based on task context. Use role_mapping below. Default to ["universal"] if unclear. Can search multiple roles when task spans domains.

**Step 3: Search previews**
Use `search_memory` with query, `roles=["detected_role", "universal"]`, `limit=20`.

Note: The `roles` parameter tells MCP which collections to search. Always include "universal" to catch cross-domain patterns.

**Step 4: Analyze previews**
Review returned previews (title + description + tags). Select 3-5 most relevant based on:
- Does title match problem domain?
- Does description indicate relevant solution?
- Do tags align with task?
- Is memory type appropriate? (episodic for debugging, procedural for workflows, semantic for patterns)

**Step 5: Retrieve full content**
Use `batch_get_memories` with selected doc_ids and `roles=["detected_role", "universal"]`.

Note: batch_get_memories needs roles parameter to know which collections to search in.

**Step 6: Present results**
Format retrieved memories clearly. Let the main agent decide what to apply.
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

Search multiple role collections when task spans domains (e.g., ["backend", "devops", "universal"] for API deployment task).
</role_mapping>
