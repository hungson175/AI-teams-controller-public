# Memory System V7 Design Alignment Review

**Reviewer**: DEV
**Date**: 2026-01-20
**Design Version**: V7
**Implementation**: Sprint 5 (Skills, Subagent, MCP)

---

## EXECUTIVE SUMMARY

**Overall Status**: ⚠️ **Partial Alignment - Critical Metadata Mismatch**

**Key Findings:**
1. ✅ **Core architecture matches** - MCP server, Qdrant, role-based collections, two-stage retrieval
2. ❌ **Critical metadata mismatch** - Skills use 7 fields, MCP enforces 3 fields (design says 3)
3. ⚠️ **Naming inconsistencies** - "project-memory-*" vs "coder-memory-*", "memory-only" vs "memory-only"
4. ⚠️ **Collection naming differs** - "{role}-patterns" vs just "{role}"
5. ✅ **Mini search engine implemented correctly** - Two-stage retrieval works as designed

**Critical Issue:**
Skills generate metadata with 7 fields (`memory_type`, `role`, `title`, `description`, `tags`, `confidence`, `frequency`), but MCP strictly enforces 3 fields (`title`, `preview`, `content`). **This will cause validation errors when skills try to store memories.**

**Bottom-Line Recommendation:**
**Fix metadata mismatch BEFORE release.** Either:
- Update skills to use 3-field metadata (matches V7 design + current MCP)
- OR update MCP to accept 7 fields (contradicts V7 design)

Decision needed: Which is correct - the design or the skills?

---

## DETAILED COMPARISON

### 1. Architecture & Components

#### ✅ What's Implemented Correctly

**MCP Server Structure:**
- FastMCP-based server ✓
- 8 tools implemented ✓
- Pydantic v2 validation ✓
- Proper logging to stderr (MCP protocol compliance) ✓

**Vector Database:**
- Qdrant on port 16333 ✓
- Role-based collections ✓
- Voyage AI embeddings (voyage-4-lite, 1024 dimensions) ✓
- Client singleton pattern ✓

**Skills & Subagent:**
- Two skills (store/recall) ✓
- Specialized subagent with MCP tools only (zero file access) ✓
- Workflow steps documented ✓

**Mini Search Engine:**
- Two-stage retrieval implemented ✓
- `search()` returns previews only (id, title, preview, score) ✓
- `batch_get_memories()` for full content ✓
- Design says "20-50 results → snippets → LLM picks 3-5 → fetch full" - **matches implementation** ✓

#### ⚠️ What's Different from Design

**Naming (Minor Issue):**

| Component | V7 Design | Implementation | Impact |
|-----------|-----------|----------------|--------|
| Store skill | `memory-store` | `memory-store` | Low - just names |
| Recall skill | `memory-recall` | `memory-recall` | Low - just names |
| Subagent | `memory-only` | `memory-only` | Low - just names |
| MCP server path | `src/qdrant_memory_mcp/__main__.py` | `src/mcp_server/server.py` | Low - works fine |

**Collection Naming (Medium Issue):**

| Aspect | V7 Design | Implementation |
|--------|-----------|----------------|
| Collection name | IS the role (e.g., "backend") | "{role}-patterns" (e.g., "backend-patterns") |
| Reason for design | "Collection name IS the role (simple, no redundancy)" | Explicitly adds "-patterns" suffix |

**Impact**: Medium. Design emphasizes simplicity. Current implementation adds redundancy. Collection names appear in:
- Skills (role_mapping shows "backend-patterns")
- Subagent docs (lists "backend-patterns", "frontend-patterns")
- MCP tools (when specifying collections)

Not broken, just inconsistent with design principle.

**Metadata Structure (CRITICAL ISSUE):**

| Source | Metadata Fields | Purpose |
|--------|----------------|---------|
| **V7 Design** | 3 fields: `title`, `preview`, `content` | "Metadata (3 fields)" explicitly stated |
| **MCP Implementation** | Enforces 3 fields: `title`, `preview`, `content` | Pydantic validator rejects others |
| **Skills (store/recall)** | 7 fields: `memory_type`, `role`, `title`, `description`, `tags`, `confidence`, `frequency` | Skills documentation shows this |

**The Problem:**

1. V7 design says metadata has **3 fields only** (lines 62-69)
2. MCP server enforces **3 fields only** (models.py lines 119-133: validates and rejects extra fields)
3. BUT skills tell agents to use **7 fields** (memory-store SKILL.md lines 52-65)

**What happens:**
- Skill invokes memory-only
- memory-only calls `store_memory(document, metadata)` with 7 fields
- MCP validator raises error: "Unauthorized metadata fields: memory_type, role, tags, confidence, frequency"
- **Storage fails**

**Why it matters:**
- Broken functionality - memories can't be stored
- Must be fixed before release
- Not discovered because no end-to-end test exists yet

---

### 2. Data Structure

**V7 Design says:**
```json
{
  "title": "FastMCP: Minimal Python MCP Server",
  "preview": "Use FastMCP for rapid prototyping...",
  "content": "[full formatted document]"
}
```

**MCP Implementation enforces:**
```python
# Boss: Metadata ONLY has title, preview, content - nothing else
allowed = {'title', 'preview', 'content'}
extra = set(v.keys()) - allowed
if extra:
    raise ValueError(f"Unauthorized fields: {', '.join(extra)}")
```

**Skills documentation says:**
```json
{
  "memory_type": "episodic|procedural|semantic",
  "role": "backend|frontend|...",
  "title": "Plain text title",
  "description": "2-3 line summary",
  "tags": ["#tag1", "#tag2"],
  "confidence": "high|medium|low",
  "frequency": 1
}
```

**Analysis:**
- Design and MCP are consistent (3 fields)
- Skills are inconsistent (7 fields)
- Skills probably written before design solidified
- Need to update skills to match design + MCP

---

### 3. Content Format

**V7 Design (lines 72-79):**
```markdown
**Title:** [title]
**Preview:** [2-3 sentence description]

**Content:** [full content]

**Tags:** #tag1 #tag2 #tag3
```

**Skills Implementation (memory-store lines 21-29):**
```markdown
**Title:** [Concise title]
**Description:** [2-3 sentence summary - CRITICAL for search]

**Content:** [What happened, tried, worked/failed, lesson]

**Tags:** #role #topic #success|#failure
```

**Differences:**
- Design: "**Preview:**" field
- Skills: "**Description:**" field

**Impact**: Low. Both are 2-3 sentence summaries. Just naming difference. Should unify to "Preview" (matches V7 + metadata field name).

---

### 4. Trigger Mechanisms (When)

**V7 Design:**

| Trigger | When | How |
|---------|------|-----|
| STORE | After task completes | Hook: `~/.claude/hooks/memory_store_reminder.py`, random 1/3 chance |
| RETRIEVE | When TodoWrite called | Hook on TodoWrite post-tool-use, invokes `memory-recall` |

**Implementation Status:**
- ✅ Skills exist (`memory-store`, `memory-recall`)
- ✅ Subagent exists (`memory-only`)
- ⚠️ Hooks not visible in reviewed files (need to check hooks directory)

**Note**: Can't verify hooks alignment without reading hook files. Assume they exist per Sprint 5 completion.

---

### 5. Role-Based Collections

**V7 Design (lines 46-50):**
- universal
- backend
- frontend
- scrum-master
- product-owner

**Skills Implementation (role_mapping):**
- universal
- backend
- frontend
- devops
- ai
- security
- mobile
- pm
- scrum-master
- qa
- quant

**Differences:**
- Design has 5 roles (minimal example)
- Implementation has 11 roles (comprehensive)

**Analysis**: Implementation expands on design. Good. Design was illustrative, not exhaustive.

---

## What's Good About Current Implementation

1. **MCP server is solid**
   - Proper FastMCP patterns
   - Clean Pydantic validation
   - Follows MCP best practices (logging to stderr)
   - 8 tools match design intentions

2. **Mini search engine works**
   - Two-stage retrieval correctly implemented
   - Preview-only search (snippets)
   - Batch fetch for selected memories
   - Matches V7 design algorithm exactly

3. **Subagent constraints enforced**
   - Zero file access (prevents context pollution)
   - MCP tools only
   - Uses fast model (haiku)
   - Design goal achieved

4. **Role-based collections**
   - Comprehensive role mapping
   - Flexible (can add more roles)
   - Search across multiple roles supported

---

## What's Bad/Problematic

### CRITICAL

1. **Metadata mismatch will break storage**
   - Skills generate 7 fields
   - MCP rejects anything except 3 fields
   - Validation error on every store attempt
   - **Must fix before release**

### MEDIUM

2. **Collection naming adds redundancy**
   - Design says: "Collection name IS the role (simple, no redundancy)"
   - Implementation: "{role}-patterns" suffix
   - Contradiction to design principle
   - Not broken, just inconsistent

3. **Naming inconsistencies**
   - `coder-memory-*` vs `project-memory-*`
   - `memory-only` vs `memory-only`
   - Pick one naming scheme and stick with it

### LOW

4. **Field naming: "Preview" vs "Description"**
   - Design + metadata: "preview"
   - Skills content format: "Description"
   - Should unify to "Preview"

---

## Specific Suggestions

### Priority 1 (CRITICAL - Must Fix)

**Fix metadata mismatch:**

**Option A (Recommended - Matches V7):**
Update skills to use 3-field metadata:
```json
{
  "title": "Short title",
  "preview": "2-3 sentence summary",
  "content": "[full formatted markdown document]"
}
```

Move `tags`, `memory_type`, etc. INTO the content markdown (already there per design).

**Option B (Not Recommended):**
Update MCP to accept 7 fields - contradicts V7 design.

**Decision needed**: Which is authoritative - V7 design or skills docs?

### Priority 2 (Should Fix)

**Simplify collection naming:**
- Remove "-patterns" suffix
- Collections: "backend", "frontend", "universal" (not "backend-patterns")
- Matches V7 design principle: "Collection name IS the role (simple, no redundancy)"

**Unify content field naming:**
- Change skills markdown format from "**Description:**" to "**Preview:**"
- Matches V7 design + metadata field name

**Standardize naming:**
- Pick: `coder-memory-*` OR `project-memory-*` (not both)
- Pick: `memory-only` OR `memory-only` (not both)
- Update all references consistently

### Priority 3 (Nice to Have)

**Add end-to-end test:**
- Test: skill → subagent → MCP → store → retrieve
- Would have caught metadata mismatch immediately
- Critical for release validation

---

## Test Coverage Gap

**Missing:**
- No end-to-end test from skill invocation through storage
- MCP unit tests exist (Sprint 4)
- Skills exist (Sprint 5)
- But no integration test linking them

**Why it matters:**
- Metadata mismatch wasn't caught
- Would fail in production
- Need integration test before release

---

## Conclusion

**Alignment Status**: ⚠️ Partial

**Core design principles implemented correctly:**
- ✅ MCP server architecture
- ✅ Two-stage retrieval (mini search engine)
- ✅ Role-based collections
- ✅ Subagent isolation (no file access)

**Critical issue preventing release:**
- ❌ Metadata structure mismatch (skills use 7 fields, MCP accepts 3)

**Recommendation:**
1. **Fix metadata immediately** - Update skills to use 3-field metadata per V7 design
2. **Simplify collection naming** - Remove "-patterns" suffix (low priority)
3. **Add integration test** - Prevent similar issues
4. **Unify naming** - Pick one scheme for skills/subagent names

**Timeline Impact:**
- Metadata fix: 1-2 hours (update 2 skill files)
- Collection naming: 30 minutes (breaking change to existing data)
- Integration test: 2-3 hours
- Naming unification: 30 minutes

**Total estimated effort to full alignment**: 4-6 hours

---

**Review Complete**: 2026-01-20 09:53
