# Packaging Agent - Claude Code Instructions

## IMPORTANT: Voice Input & Translation

**Boss primarily uses voice interaction. Expect:**
- Typos from speech-to-text transcription
- Non-native English pronunciation errors
- Vietnamese to English translation mistakes
- Be EXTREMELY careful interpreting context and intent

**When unclear, ask for clarification instead of guessing.**

---

## Project Overview

Packaging the AI Teams Controller system for public release. Ship by 11:59 PM TODAY.

**Mission**: Ship raw truth, not perfect theory. Proof beats pitch.

---

## CRITICAL: Memory System Implementation

### Reference Project (READ-ONLY)

**Reference Location**: `/home/hungson175/dev/deploy-memory-tools/`

**⚠️ IMPORTANT - READ THIS CAREFULLY:**

1. **REFERENCE ONLY** - This project is for reading and learning, NOT for modification
2. **NOT GROUND TRUTH** - The implementation has issues ("a lot of the implementation is bullshit")
3. **READ-ONLY** - Never modify files in deploy-memory-tools/
4. **Design First** - When building memory system:
   - Review reference to understand what exists
   - Design step-by-step plan
   - Present plan to Boss for approval
   - Wait for explicit approval
   - Implement in packaging-agent project (THIS project), not reference
5. **Never assume** - Don't assume reference is correct. Use it to learn, not copy.

### Target Specification (THE GOAL)

**Main Spec**: `/home/hungson175/dev/coding-agents/packaging-agent/memory-system/docs/tech/memory_guide_draft_v7.md`

**This is what we're building toward:**
- Follow v7 spec for end goal
- Implement progressively with Boss review at each step
- Boss approves each sprint before proceeding to next
- Each sprint builds incrementally toward v7 spec

### Workflow for Memory System Implementation

1. DEV reviews reference project → reports findings
2. PO designs SMALL sprint plan (progressive development)
3. PO presents plan to Boss for review
4. Boss approves/modifies plan
5. Execute sprint in packaging-agent project only
6. Boss validates sprint deliverables
7. Repeat for next sprint

**PROGRESSIVE DEVELOPMENT:**
- Sprints must be TINY (1-2 hours each)
- Each sprint independently testable
- Boss review after each sprint
- Build toward v7 spec incrementally

**This instruction persists across auto-compact. Do not forget.**

---

## Team Structure

3-role tmux team:
- **PO (Product Owner)**: Coordinates packaging, manages backlog, assigns tasks
- **DEV (Developer)**: Implements code, scripts, installers
- **DU (Document Updater)**: Writes documentation, README, release notes

**Communication**: Use `tm-send ROLE "message"` for all team communication

---

## Time Constraint

**Deadline**: 11:59 PM TODAY
**Approach**: NO refactoring, NO redesign, NO improvements unless directly needed for shipping

---

## Key Files

- **BACKLOG.md**: `docs/tmux/packaging-agent/BACKLOG.md` - All tasks and priorities
- **WHITEBOARD.md**: `docs/tmux/packaging-agent/WHITEBOARD.md` - Current status
- **EPIC (Memory)**: `docs/tmux/packaging-agent/epics/EPIC_MEMORY_SYSTEM.md`
- **Demo Script**: `docs/demo-script/v1-demo-script.md`

---

## Components Status

1. **tmux Team Creator Skill**: ✅ COMPLETE (ready for distribution)
2. **Memory System**: 🔄 IN DESIGN (reference reviewed, awaiting implementation plan)
3. **Web UI**: ⏳ SQLite conversion needed (P1, if time allows)

---

## P0 Tasks (Must Ship)

1. **Demo Video** (60 min) - MANDATORY
   - 30 seconds, technical tone
   - 2 features: Scrum team working + self-improving memory
   - Script ready at docs/demo-script/v1-demo-script.md

2. **README Finalization** (30 min) - Required for ship
   - Add memory system details after implementation

---

**Last Updated**: 2026-01-19 20:06
**Critical Reminder**: Memory reference is NOT ground truth. Design first, get approval, implement in THIS project.
