# Sprint 5: Package Memory System Skills & Dependencies

**Sprint Goal**: Complete self-contained packaging - install once, everything works immediately

**Problem**: Memory System currently depends on external skills and subagents NOT packaged in this repository

---

## Current Issues

### Issue 1: External Skills Dependencies
Memory System requires:
- `memory-store` (in ~/.claude/skills/ - NOT packaged)
- `memory-recall` (in ~/.claude/skills/ - NOT packaged)

**Problem**: User installs this package but skills don't exist → System doesn't work

### Issue 2: External Subagent
Memory skills use `subagent_type: "memory-only"` which is:
- Defined externally (not in this package)
- Not installed by install-memory-system.sh

**Problem**: Subagent not available → Skills can't spawn memory-only agent

### Issue 3: Hooks Not Packaged
Memory hooks (if any) like `memory_store_reminder.py` not included

**Problem**: Automation doesn't work without hooks

---

## Sprint 5 Deliverables

### Deliverable 1: Package Memory Skills (NEW)
Create NEW skills specific to this package (reference old ones):

**File Structure**:
```
memory-system/skills/
├── memory-store/
│   └── SKILL.md
└── memory-recall/
    └── SKILL.md
```

**Requirements**:
- NEW skill names: `memory-store`, `memory-recall`
- Reference original skills but adapted for this package
- Self-contained (no external dependencies)
- Work with packaged MCP server

### Deliverable 2: Package Memory Subagent
Create NEW subagent definition for this package:

**File Structure**:
```
memory-system/subagents/
└── memory-only/
    ├── SUBAGENT.md (or config.json)
    └── README.md
```

**Requirements**:
- NEW subagent name: `memory-only` (or similar)
- Reference original `memory-only` subagent
- Tools: ONLY MCP memory tools (no Read/Write/Edit/Glob/Bash)
- Packaged in this repository

### Deliverable 3: Package Hooks (If Needed)
If automation requires hooks:

**File Structure**:
```
memory-system/hooks/
└── memory_store_reminder.py
```

**Requirements**:
- Include hooks needed for memory automation
- Installation script installs them

### Deliverable 4: Update Installation Script
Modify `install-memory-system.sh` to install:
- MCP server (already done)
- NEW memory skills → user's ~/.claude/skills/
- NEW subagent → appropriate location
- Hooks → ~/.claude/hooks/ (if needed)

**Requirements**:
- One command: `./install-memory-system.sh`
- Installs everything
- User can immediately use memory system
- No manual configuration

### Deliverable 5: Update Documentation
Update INSTALLATION.md and README to reflect:
- Skills installation
- Subagent installation
- What gets installed where
- How to verify skills work

---

## Technical Requirements

### Skill Requirements
- Must use packaged MCP server (not external)
- Must spawn packaged subagent (not external)
- Must be installable via script
- Must work immediately after installation

### Subagent Requirements
- ZERO access to file tools (Read, Write, Edit, Glob, Bash)
- ONLY MCP memory tools access
- Prevents context pollution (design goal)
- Clear separation from main agent

### Installation Requirements
- Idempotent (safe to run multiple times)
- Clear feedback (what's being installed where)
- Verification step (test skills work)
- Uninstallation instructions

---

## References

### Original Skills
- `~/.claude/skills/memory-store/` (reference for NEW skill)
- `~/.claude/skills/memory-recall/` (reference for NEW skill)

### Original Subagent
- `memory-only` subagent definition (reference for NEW subagent)

**Boss directive**: Reference old skills/subagent but create NEW ones for this package

---

## Acceptance Criteria

1. ✅ NEW skills created (`memory-store`, `memory-recall`)
2. ✅ NEW subagent defined and packaged
3. ✅ Installation script installs skills + subagent + hooks
4. ✅ One command: `./install-memory-system.sh` → everything works
5. ✅ User can immediately use memory system after install
6. ✅ Documentation updated
7. ✅ Verification tests pass (skills callable, subagent spawnable)

---

## Success Criteria

**Fresh install test**:
```bash
# User with empty system
./install-memory-system.sh

# Result:
# - MCP server configured
# - Skills installed in ~/.claude/skills/
# - Subagent available
# - Hooks installed (if needed)
# - User can immediately invoke skills
```

**Zero external dependencies** - Everything self-contained in this package

---

## Next Steps

1. DEV: Research original skills/subagent structure
2. DEV: Create NEW packaged skills (reference old ones)
3. DEV: Create NEW packaged subagent
4. DEV: Update install-memory-system.sh
5. DEV: Test full installation on clean system
6. DU: Update documentation
7. PO: Independent verification
8. Report to Boss

---

**Sprint 5 Start**: Now
**Estimated Complexity**: High (packaging dependencies, new skills, subagent)
**Critical**: This is P0 - blocks public distribution
