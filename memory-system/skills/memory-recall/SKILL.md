---
name: memory-recall
description: Retrieve coding patterns from GLOBAL vector database (cross-project learning). Auto-invokes when TodoWrite has >3 tasks or when user says "--recall". Searches relevant role collections based on task context.
---

<execution>
Use Task tool with `subagent_type: "memory-only"` to keep main context clean.

The memory-only agent has ZERO access to Read/Write/Edit/Glob/Bash - it can ONLY use MCP memory tools. This prevents file reading pollution by design.
</execution>

<selectivity>
Search when: Non-obvious bugs, complex architectures, performance issues, unfamiliar domains, hard problems.

Skip when: Obvious tasks, basic file operations, standard workflows, problems solvable with basic knowledge.

**Hook Activation Condition:**
- TodoWrite tasks >3: Activate memory-recall (complex task needs context)
- TodoWrite tasks ≤3: Don't activate (simple task, no need)
- One search PER TASK in TodoWrite (e.g., 4 tasks = 4 searches)
</selectivity>

<workflow>
**Step 1: Build semantic query**
Construct 5-10 sentences with full problem description (not too short, not too long):
- What is the problem?
- What is the technical context?
- What outcome is desired?
- What have you tried?
- What are the constraints?

Example: "Need to implement rate limiting for REST API to prevent abuse. Backend service in Node.js with Express. Want proven pattern that prevents thundering herd. Current setup uses Redis for session storage. Need to rate limit by IP address with 100 requests per minute. Must handle distributed deployments with multiple server instances. Looking for battle-tested implementation that won't add significant latency."

**Step 2: Detect relevant roles**
Determine which role collections to search based on task context. Use role_mapping below. Default to ["OTHER"] if unclear. Can search multiple roles when task spans domains.

**Step 3: Search previews**
Use `search_memory` with query, `roles=["detected_role", "OTHER"]`, `limit=30`.

Note: The `roles` parameter tells MCP which collections to search.

**Step 4: Analyze previews**
Review returned previews (preview text ONLY). Select 3-5 most relevant based on:
- Does preview indicate relevant solution?
- Does preview match problem domain?

Note: Score doesn't matter - don't trust similarity scores. Focus on analyzing the preview text content.

**Step 5: Retrieve full content**
Use `batch_get_memories` with selected doc_ids and `roles=["detected_role", "OTHER"]`.

Note: batch_get_memories needs roles parameter to know which collections to search in.

**Step 6: Present results**
Format retrieved memories clearly. Let the main agent decide what to apply.
</workflow>

<role_mapping>
Available roles (maps to Qdrant collections):
- backend: API, endpoint, database, server, auth
- frontend: React, Vue, component, UI, CSS
- devops: Deploy, Docker, Kubernetes, CI/CD
- scrum-master: Agile, sprint, standup, retrospective, planning
- qa: Testing, quality assurance, verification, validation
- OTHER: General patterns, cross-domain knowledge

Default to "OTHER" if unclear. Each role corresponds to a separate Qdrant collection.

Search multiple role collections when task spans domains (e.g., ["backend", "devops", "OTHER"] for API deployment task).
</role_mapping>
