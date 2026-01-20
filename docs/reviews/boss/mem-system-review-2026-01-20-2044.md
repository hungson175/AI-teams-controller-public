# Memory System Architecture Review

**Reviewer**: Boss (Hung Son)
**Date**: 2026-01-20 20:44 - 21:15
**Review Session**: Memory Skills & Subagent Architecture

---

## Components Under Review

1. **memory-store** skill (was coder-memory-store)
2. **memory-recall** skill (was coder-memory-recall)
3. **memory-only** subagent
4. V7 Design Alignment Review

---

## Review Questions

1. Is using MCP for memory skills stable enough? **→ YES**
2. Is using subagent approach stable enough? **→ YES**
3. What is the ROM of the memory-only subagent? **→ ONLY MCP memory tools, zero file access**
4. Should we keep current architecture or redesign? **→ KEEP with fixes below**

---

## Boss Review Notes

### OVERALL ASSESSMENT

**Architecture**: Approved with fixes
- MCP approach: ✅ Stable enough
- Subagent approach: ✅ Stable enough
- memory-only ROM: ✅ Correct (MCP tools only, zero file access)

**Status**: APPROVED after critical fixes applied

---

## Critical Issues Found & Fixed

### 1. memory-only Subagent (FIXED - commit d2c3252)

**Issues**:
- ❌ Role collections COMPLETELY WRONG (old copied code)
  - Had: universal, backend-button, frontend-button, -patterns suffixes
  - Should be: scrum-master, frontend, backend, qa, OTHER
- ❌ Metadata structure WRONG (7 fields instead of 3)
  - Boss: "I've told you countless times - only title, preview, content"
- ❌ Missing content format guidance

**Fixes Applied**:
- ✅ Corrected role collections to actual tmux team roles
- ✅ Fixed metadata to 3 fields ONLY (title, preview, content)
- ✅ Added complete content format example with Title+Preview+Content+Tags
- ✅ Emphasized tags go INSIDE content (NOT in metadata)

---

### 2. memory-recall Skill (FIXED - commit ecc2bbf)

**Issues**:
- ❌ Query too short (2-3 sentences)
- ❌ Search limit too low (20)
- ❌ Default role wrong (universal instead of OTHER)
- ❌ Analyzing score (Boss doesn't trust similarity scores)
- ❌ Role mapping wrong (universal, ai, security, mobile, pm, quant, -patterns)
- ❌ Missing hook activation condition

**Fixes Applied**:
- ✅ Query: 2-3 sentences → **5-10 sentences** (full problem description)
- ✅ Limit: 20 → **30**
- ✅ Default role: universal → **OTHER**
- ✅ Step 4: Preview ONLY analysis (removed score trust)
- ✅ Role mapping: backend, frontend, devops, scrum-master, qa, OTHER
- ✅ Hook condition documented: TodoWrite >3 tasks activates, ≤3 doesn't
- ✅ One search PER TASK in TodoWrite

**Boss quote**: "Score doesn't matter - don't trust similarity scores. Focus on preview."

---

### 3. memory-store Skill (TO BE FIXED)

**Issues to Fix**:

**A. Selectivity Section - ADD EMPHASIS:**
- Extremely selective
- Most of time: DOESN'T insert
- Safe: <1 insertion per task
- 2-3 insertions almost NEVER happen

**B. Workflow Fixes:**

**Step 3 & 4**: universal → OTHER (same error as memory-recall)

**MISSING STEP between 4 and 5**:
- After search gets previews (Step 4)
- LLM reads previews, selects 3-4 that might match/conflict
- **FETCH those specific ones** (not all 10)
- Read fetched content to decide: duplicate? merge? update?
- **Emphasize**: Don't rely on similarity score - rely on LLM review of fetched content

**Step 6 - store_memory API** (verified from MCP code):
```python
store_memory(
    document: str,      # Full markdown formatted text
    role: str,          # Collection name (backend, frontend, qa, OTHER)
    metadata: {         # 3 fields ONLY
        title: str,
        preview: str,
        content: str
    }
)
```

Current skill incorrectly shows `document` and `metadata` as confusing.
Need to clarify:
- `document` = full markdown text (Title + Preview + Content + Tags)
- `role` = collection name (backend, frontend, qa, OTHER, etc.)
- `metadata` = {title, preview, content} - 3 fields extracted from document

**C. Role Mapping:**
- No universal → OTHER
- Roles must match tmux team: frontend, backend, scrum-master, po, qa, OTHER
- Note: Can add roles via MCP tool

**D. Frustration Signals - MOVE TO TOP:**
- Move to skill description (frontmatter at top of file)
- Words that trigger: fuck, bitch, dog, bad words
- These words = signal to possibly call memory-store

---

### 4. Skill Naming (TO BE FIXED)

**Issue**: Current names would duplicate Boss's existing skills

**Boss directive**: Rename to simpler names
- coder-memory-store → **memory-store**
- coder-memory-recall → **memory-recall**

**Impact**: Must update all references
- Skill directories
- Skill frontmatter (name field)
- Subagent memory-only.md description
- Install script (install-memory-system.sh)
- Hooks (memory_store_reminder.py, todowrite_memory_recall.py)
- Documentation (INSTALLATION.md, README)

---

## Review Outcome

**DECISION**: APPROVE architecture with fixes

**Architecture approved**:
- ✅ MCP for memory skills: Stable
- ✅ Subagent approach: Stable
- ✅ memory-only subagent ROM: Correct (MCP tools only, zero file access)

**Fixes required**:
1. ✅ memory-only subagent (DONE - commit d2c3252)
2. ✅ memory-recall skill (DONE - commit ecc2bbf)
3. ⏳ memory-store skill (IN PROGRESS)
4. ⏳ Skill renaming (IN PROGRESS)

**Next Steps**:
1. Fix memory-store skill per review notes above
2. Rename skills: coder-memory-* → memory-*
3. Update all references in install script, hooks, docs
4. Final verification

---

**Review Complete**: 2026-01-20 21:15
**Status**: Architecture APPROVED, implementation fixes in progress

