# Product Backlog - Packaging Agent Team

**Owner**: PO
**Mission**: Ship AI Teams Controller
**Last Updated**: 2026-01-20 07:15

---

## P0 - MUST DO (Prevents Ship)

### Pre-Publishing Checklist
Complete ALL items before public distribution: API keys, memory system, README, sensitive file cleanup, installation scripts, demo materials, final testing, GitHub setup.
**Details**: `backlog/pre-publishing-checklist.md`

### Generate Test API Keys
Boss: Generate 6 test API keys (xAI, Soniox, Voyage, Google TTS, OpenAI, HD-TTS) with PREPAID/spending limits, prefix with "TO-BE-REMOVED", commit to repo for easy public testing.
**Details**: `backlog/api-keys-generation.md`

### xAI Email
Send to xAI team: Brief intro + annotated screenshot + demo video (delegated to friend) + GitHub link.
**Details**: `/home/hungson175/dev/coding-agents/packaging-agent/docs/XAI_EMAIL_REMINDER.md`

### LinkedIn Post
DU writes technical post for xAI/recruiters showcasing demo. Target audience: Professional devs with 3+ months coding agent experience (NOT hobbyists).
**Priority**: P0 | **Time**: 20 min

### README Finalization
Rewrite V6 README (Boss: "pretty shitty"). Fix installation instructions, add memory system section, verify all paths. Use v5 as base.
**Priority**: P0 | **Time**: 30+ min | **Blocker**: Memory system completion

---

## P1 - SHOULD DO (Required for MVP)

### CRITICAL REVIEW: Memory Skills Implementation
**Boss reminder**: Review project-memory-store and project-memory-recall implementation carefully.

**Important**: These were NOT just copied from coder-memory-* - there's a reason for rewrite.

**Questions Boss needs to answer during review**:
1. Is using MCP for memory skills stable enough?
2. Is using subagent approach stable enough?
3. What is the ROM (role/responsibility) of the memory-agent subagent?
4. Should we keep current architecture or redesign?

**Current Implementation** (Sprint 5):
- project-memory-store: Uses Task tool → memory-agent subagent → MCP tools
- project-memory-recall: Uses Task tool → memory-agent subagent → MCP tools
- memory-agent: ONLY has MCP memory tools (zero file access)

**Action**: Boss to review before finalizing packaging
**Priority**: P1 - Blocks finalization
**Location**: memory-system/skills/, memory-system/subagents/

---

### Component 1: Cleanup Team Templates
Remove unnecessary team templates from tmux-team-creator skill:
- ❌ Remove: Game Development team
- ❌ Remove: Packaging team
- ✅ Keep only: Scrum team, Light team, Research team (3 teams total)
**Reason**: Simplify skill, focus on core templates
**Priority**: P1

### Package Global Skills into tmux-team-creator
Bundle global skills INSIDE tmux-team-creator folder as subfolder. One installer installs everything.

**Structure**:
```
tmux-team-creator/
├── install-tmux-skill.sh (installs tmux skill + all global skills)
├── tmux-team-creator.skill
├── tm-send
└── skills/ (subfolder with global skills to bundle)
    ├── quick-research/
    ├── webapp-testing/
    ├── android-app-testing/ (if available)
    ├── llm-apps-creator/
    ├── power-agent-creator/
    ├── pdf/ (Anthropic)
    └── docx/ (Anthropic)
```

**Installer updates**:
- Copy skills/* to ~/.claude/skills/ (all at once)
- Verify all skills installed

**Goal**: One command (`./install-tmux-skill.sh`) installs tmux-team-creator + all bundled skills
**Priority**: P1 | **Effort**: 2-3 hours

### Spec Lock for Skills
Implement "spec lock" mechanism to make team run smoothly:
- Lock skill specifications to prevent drift
- Ensure consistent behavior across team members
- Related to skills coordination
**Details**: Boss to clarify exact requirements
**Priority**: P1

### Component 1: tmux Team Creator
✅ COMPLETE (Sprint 6 Track A): Professional installer (275 lines), colored output, verification, prerequisites check. Documentation complete.

### Component 2: Memory System
✅ COMPLETE (Sprint 1-5): MCP server, installation script, skills, subagent, hooks all packaged. Zero external dependencies.

### Component 3: Web UI
✅ COMPLETE (Sprint 6 Track B): SQLite demo mode, test@example.com/test123 user, no PostgreSQL required. Documentation complete.

---

## P2 - NICE TO HAVE (Skip Unless Time Allows)

### Agent Team Value Proposition Document
DU writes explanation of how agent teams work and why valuable (multi-agent coordination, self-improvement, scrum adaptation, voice, progressive disclosure).
**Content ideas**: `docs/ideas/agent-team-value-proposition.md`

### Qdrant Docker Data Loss Research
DU researches why Qdrant in Docker loses data on unexpected shutdown. Document Docker volume persistence and buffer/RAM settings.
**Deliverable**: `docs/research/qdrant-docker-data-loss.md`

### Demo Video
30s technical demo delegated to friend. Call at 23:00 if not received.

### Memory Generalization Research
Research mechanism to generalize episodic memories into semantic patterns (e.g., multiple JWT bugs → general JWT pattern). Post-ship research.

### Unlock X Account
Contact X support to unlock suspended account. Too complicated for tonight - LinkedIn sufficient.

### CLI: Project-Specific Scrum Team Creator
Create command to generate customized Scrum teams based on project type. Post-ship feature.

### One-Command Init (npx create-tmux-team)
Post-launch feature - skip for initial ship.

### Chatbot on Web UI
Popup chatbot to guide users. Post-launch.

### Boss Verification Tasks
Verify tmux-team-creator skill packaging, test install script, verify all 5 templates work.

---

## P3 - POST-LAUNCH

### Overall Integration Test (Docker)
After ALL components complete: Full integration test in isolated Docker container. Steps: Create Docker on this machine → git clone repo → Follow README installation → Use `--extract dangerously skip permissions` → Verify all 3 components work. Tests real user experience from scratch.
**Priority**: P3 | **When**: After all packaging complete

- PostgreSQL support documentation
- Docker-based installation option
- CI/CD pipeline for releases
- Automated testing for installers
- Advanced documentation
- Code cleanup and polish

---

## Critical Context

**Mission**: Ship as proof of work for job applications (xAI, Axon ASOM, international contracts)

**Constraints**:
- NO refactoring
- NO redesign
- NO improvements unless directly needed for shipping
- Ship raw truth, not perfect theory
- Proof beats pitch

**Coordination**:
- When memory system complete → Report to Boss AND `tm-send -s packaging-comandcenter PO "message"`

---

## Notes

- **NEVER TOUCH**: Original project at `/home/hungson175/dev/coding-agents/AI-teams-controller`
- **WORK ON**: Public fork at `/home/hungson175/dev/coding-agents/AI-teams-controller-public`
- Code split across 3 projects: UI, Agent skills/prompts, Memory system
- Focus: Package existing code, clean sensitive data, create demo video

---

## Design Notes (Non-Actionable Reminders)

### Port Assignment Policy - CRITICAL
**NEVER use standard ports** (3000, 8000, 5000, etc.) - they WILL conflict with users' existing programs.

**Always use weird, unusual ports**:
- Frontend: 333X range (avoid 3334 - Boss's existing)
- Backend: 170XX range (avoid 17061, 17071 - Boss's existing)

**MANDATORY**: Document ALL ports in README installation instructions.

**Current assignments**:
- Memory System: Qdrant 16333
- Web UI Frontend: 3337
- Web UI Backend: 17063

---

## Design Notes (Non-Actionable Reminders)

### Docker/Docker Compose Packaging - NOT NOW
**Reminder**: If considering Docker/Docker Compose packaging in future versions - be cautious. Entire system is tmux-based (multi-session coordination). Running tmux sessions inside Docker not tested yet, likely has issues. **Avoid Docker packaging for now.** Consider for later versions only after thorough testing.

---

**Priority Framework**:
- **P0**: Blocker preventing ship → Must do
- **P1**: Required for MVP → Do if time allows
- **P2**: Nice to have → Skip if time tight
- **P3**: Post-launch → After successful ship
