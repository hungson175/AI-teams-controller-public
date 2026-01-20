# Sprint 5 Research Findings

**Date**: 2026-01-20 08:02
**Researcher**: DEV
**Phase**: Research Phase Complete

---

## Original Skills Analysis

### 1. coder-memory-store

**Location**: `~/.claude/skills/coder-memory-store/SKILL.md`

**Structure**:
```markdown
---
name: coder-memory-store
description: [One-line description]
---

<execution>
Use Task tool with `subagent_type: "memory-only"`
[Explanation of zero file access design]
</execution>

<selectivity>
[When to store, when to skip]
</selectivity>

<workflow>
[6-step workflow for storing memories]
</workflow>

<role_mapping>
[Available roles and collection mapping]
</role_mapping>

<frustration_signals>
[Detection of learning moments]
</frustration_signals>
```

**Key Features**:
- Uses Task tool to spawn memory-only subagent
- 6-step workflow: Format → Extract metadata → Detect role → Search duplicates → Decide action → Store
- Metadata structure: memory_type, role, title, description, tags, confidence, frequency
- 11 role collections: universal, backend, frontend, devops, ai, security, mobile, pm, scrum-master, qa, quant

### 2. coder-memory-recall

**Location**: `~/.claude/skills/coder-memory-recall/SKILL.md`

**Structure**: Similar to store with different workflow

**Key Features**:
- Uses Task tool to spawn memory-only subagent
- 6-step workflow: Build query → Detect roles → Search previews → Analyze → Retrieve full → Present
- Same role_mapping as store
- Multi-role search capability

---

## Subagent Analysis

### memory-only Subagent

**Location**: `~/.claude/agents/memory-only.md`

**Frontmatter**:
```yaml
---
name: memory-only
description: [Description for Task tool]
tools: mcp__memory__search_memory, mcp__memory__get_memory, mcp__memory__batch_get_memories, mcp__memory__store_memory, mcp__memory__update_memory, mcp__memory__delete_memory, mcp__memory__list_collections
model: haiku
color: blue
---
```

**Content Structure**:
- Critical constraints section (what agent CANNOT do)
- Tool list (what agent CAN do)
- Why constraints exist (design rationale)
- Memory levels section (role-based collections)
- Workflow guidelines (search/recall vs storage)
- Required metadata format
- Help message

**Key Design**:
- ZERO access to Read/Write/Edit/Glob/Bash (by tool restriction)
- ONLY 7 MCP memory tools
- Uses haiku model (cost optimization)
- Blue color (visual identification)

---

## Hooks Analysis

### 1. memory_store_reminder.py

**Type**: Stop hook
**Location**: `~/.claude/hooks/memory_store_reminder.py`

**Function**:
- Triggers on Stop event (33% probability)
- Reminds Claude to check if learnings should be stored
- Blocks stop with reminder message
- State tracking to prevent spam

**Key Features**:
- Random probability: 1/3 execution rate
- Cooldown disabled for tmux workflow
- State file: ~/.claude/memory_store_hook_state.json
- Safety checks to prevent infinite loops

**Decision Logic**:
```python
should_remind = (
    random.random() < 1/3 AND
    NOT stop_hook_active AND
    NOT within_cooldown
)
```

### 2. todowrite_memory_recall.py

**Type**: PostToolUse:TodoWrite hook
**Location**: `~/.claude/hooks/todowrite_memory_recall.py`

**Function**:
- Triggers on first TodoWrite call (oldTodos empty)
- Blocks with instruction to invoke coder-memory-recall
- Ensures memories are recalled when planning complex tasks

**Key Features**:
- First-call detection: oldTodos.length == 0
- No cooldown (triggers every new task)
- Simple and focused

---

## Adaptation Requirements

### For Skills

**Create NEW skills** (not copies):
- `coder-memory-store` (adapted from coder-memory-store)
- `coder-memory-recall` (adapted from coder-memory-recall)

**Changes needed**:
1. Rename in frontmatter
2. Update description to reference THIS package
3. Keep same workflow structure
4. Keep same role_mapping
5. Reference packaged MCP server (implicit via installed server)
6. Reference packaged subagent (change subagent_type name if needed)

### For Subagent

**Create NEW subagent**:
- Name: `memory-only` (or `project-memory-only`)
- Location: `memory-system/subagents/memory-only/`

**Changes needed**:
1. New name in frontmatter
2. Same tool list (7 MCP memory tools)
3. Same constraints (zero file access)
4. Same model (haiku)
5. Update description to reference THIS package

### For Hooks

**Package both hooks**:
- `memory-system/hooks/memory_store_reminder.py`
- `memory-system/hooks/todowrite_memory_recall.py`

**Changes needed**:
1. Update skill references: coder-memory-store → coder-memory-store
2. Update skill references: coder-memory-recall → coder-memory-recall
3. Keep all other logic unchanged
4. Install to ~/.claude/hooks/ during installation

---

## Installation Requirements

### Skills Installation
```bash
# Copy to user's skills directory
cp -r memory-system/skills/coder-memory-store ~/.claude/skills/
cp -r memory-system/skills/coder-memory-recall ~/.claude/skills/
```

### Subagent Installation
```bash
# Copy to user's agents directory
cp memory-system/subagents/memory-only/memory-only.md ~/.claude/agents/
```

### Hooks Installation
```bash
# Copy to user's hooks directory
cp memory-system/hooks/*.py ~/.claude/hooks/
chmod +x ~/.claude/hooks/memory_*.py
```

---

## File Structure Plan

```
memory-system/
├── skills/
│   ├── coder-memory-store/
│   │   └── SKILL.md              # Adapted from coder-memory-store
│   └── coder-memory-recall/
│       └── SKILL.md              # Adapted from coder-memory-recall
├── subagents/
│   └── memory-only/
│       ├── memory-only.md       # Subagent definition (frontmatter + content)
│       └── README.md             # Explanation for users
├── hooks/
│   ├── memory_store_reminder.py  # Stop hook (adapted)
│   └── todowrite_memory_recall.py # TodoWrite hook (adapted)
└── install-memory-system.sh      # Updated to install all above
```

---

## Key Insights

1. **Subagent naming**: Can use any name, just update `subagent_type` parameter in skills
2. **Tool restrictions**: Subagent constraints enforced by tools list in frontmatter
3. **MCP server**: Skills/subagent will use whatever MCP server is configured in ~/.claude/mcp.json
4. **Hooks are optional**: System works without hooks, but automation is better with them
5. **Idempotent installation**: All cp commands should check if files exist first

---

## Next Steps

1. ✅ Research complete (this document)
2. Create skills (coder-memory-store, coder-memory-recall)
3. Create subagent (memory-only)
4. Package hooks (adapted for new skill names)
5. Update install-memory-system.sh
6. Test full installation
7. Update documentation

---

**Research Status**: ✅ COMPLETE
**Ready for**: Implementation Phase
**Report to**: PO
