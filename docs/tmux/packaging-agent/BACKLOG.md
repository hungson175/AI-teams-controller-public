# Product Backlog - Packaging Agent Team

**Owner**: PO
**Mission**: Ship AI Teams Controller by 11:59 PM TODAY
**Time Left**: ~4.5 hours
**Last Updated**: 2026-01-19 18:45 (Transfer from packaging-comandcenter)

---

## P0 - MUST DO (Prevents Ship)

### 0. Pre-Publishing Checklist - CRITICAL
**Complete ALL items below before public distribution**

- [ ] **1. API Keys Generated** (see item 0a below for details)
  - [ ] xAI key created and added to .env
  - [ ] Soniox key created and added to .env
  - [ ] Voyage AI key created and added to .env
  - [ ] Google Cloud TTS service account created and JSON added
  - [ ] OpenAI key created and added to .env
  - [ ] All keys prefixed with "TO-BE-REMOVED" comments
  - [ ] Provider console reminders set (delete after testing period)

- [ ] **2. Memory System Complete**
  - [ ] Sprint 4 MCP server implemented and tested
  - [ ] Installation script created (fully automated)
  - [ ] Documentation added to README
  - [ ] Qdrant setup automated (Docker or standalone)
  - [ ] Test: Fresh install on clean Docker should work immediately

- [ ] **3. README Finalized**
  - [ ] v6 README reviewed and rewritten (Boss: "V6 overall pretty shitty")
  - [ ] Memory system section added
  - [ ] Installation instructions tested and validated
  - [ ] Target audience clearly stated
  - [ ] All file paths verified

- [ ] **4. Sensitive Files Removed**
  - [ ] CLAUDE.md removed from project root
  - [ ] Any .claude/ directories with sensitive info cleaned
  - [ ] No personal data in committed files
  - [ ] Check for hardcoded credentials

- [ ] **5. Installation Scripts**
  - [ ] tmux-team-creator skill installer works
  - [ ] Memory system installer works (zero manual setup)
  - [ ] Web UI installer works (SQLite demo mode)
  - [ ] All scripts tested on clean environment

- [ ] **6. Demo Materials Ready**
  - [ ] Demo video received from friend (30s)
  - [ ] Screenshots prepared
  - [ ] LinkedIn post drafted

- [ ] **7. Final Testing**
  - [ ] Boss: Fresh Docker test (read README, Claude Code auto-installs)
  - [ ] All 3 components install and run
  - [ ] No manual configuration required
  - [ ] Error handling graceful

- [ ] **8. GitHub Repository**
  - [ ] All commits pushed
  - [ ] Repository set to public
  - [ ] License added
  - [ ] Contributing guidelines (if applicable)

**Status**: Template created - items to be checked off during execution
**Owner**: Team (coordinated by PO)
**Critical**: Nothing ships until ALL items checked

### 0a. Generate Test API Keys for Public Distribution - CRITICAL
- [ ] **Generate NEW test API keys** (all prefixed with "TO-BE-REMOVED-" in comments)
- [ ] **⚠️ CRITICAL: Boss reminder - CHECK ALL KEYS ARE PREPAID, NOT POSTPAID**
  - **Why critical**: Postpaid keys with public access = unlimited bill drain
  - **Action**: Verify each key has spending limits/prepaid balance BEFORE adding to repo
  - **Safety**: Set low spending caps ($5-10) on all test keys
- [ ] **Keys to generate** (Boss: remind me to create these):
  1. **XAI_API_KEY** - xAI API for Grok LLM (⚠️ CHECK: PREPAID or spending limit)
  2. **SONIOX_API_KEY** - Soniox speech recognition (⚠️ CHECK: PREPAID or spending limit)
  3. **VOYAGE_API_KEY** - Voyage AI embeddings (⚠️ CHECK: PREPAID or spending limit)
  4. **GOOGLE_APPLICATION_CREDENTIALS** - Google Cloud TTS (⚠️ CHECK: PREPAID or spending limit)
  5. **OPENAI_API_KEY** - OpenAI (⚠️ CHECK: PREPAID or spending limit)
  6. **HDTTS_API_KEY** - HD-TTS self-hosted (⚠️ CHECK: PREPAID or spending limit)
- [ ] **Update files with test keys**:
  - `AI-teams-controller-public/backend/.env` (NOT .gitignored - for testing)
  - `memory-system/.env` (NOT .gitignored - for testing)
  - Add comments: `# TO-BE-REMOVED: Temporary test key, will be deleted after public testing period`
- [ ] **Security note**: These are TEMPORARY test keys for public testing
- [ ] **Provider Console Tracking** (Boss: add to-do in all 4 consoles):
  - xAI Console: Add reminder "Delete TO-BE-REMOVED test key after public testing"
  - Soniox Console: Add reminder "Delete TO-BE-REMOVED test key after public testing"
  - Voyage AI Console: Add reminder "Delete TO-BE-REMOVED test key after public testing"
  - Google Cloud Console: Add reminder "Delete TO-BE-REMOVED service account after public testing"
- [ ] **Commit keys to repo** (NOT gitignored - intentional for easy public testing)
- [ ] **Boss action after testing period**: Delete all test keys from provider consoles
- **Priority**: P0 - Required before ANY public distribution
- **Time**: 30 minutes (key generation + file updates)
- **Why NOT gitignored**: Users can test immediately without configuring their own keys
- **Deletion timeline**: After public testing period, Boss deletes all test keys

### 0b. xAI Email Reminder
**See**: `/home/hungson175/dev/coding-agents/packaging-agent/docs/XAI_EMAIL_REMINDER.md`

Format:
1. Very short intro (2-3 sentences)
2. Annotated screenshot of working Web UI (team structure + how it works)
3. Demo video link (30s) - **Delegated to friend, call at 23:00 if needed**
4. GitHub repo link

### 1. LinkedIn Post - 20 min
- [ ] **DU: Write LinkedIn post** to showcase demo video
- [ ] Goal: Three birds one stone - xAI (primary), Axon/ASOM, international recruiters
- [ ] Tone: Technical, straightforward (not marketing hype)
- [ ] Format: Keep concise and short (LinkedIn/Facebook)
- [ ] Include: Demo video link, GitHub repo, brief description
- [ ] Use relevant hashtags: #xAI, #Macrohard, #AutonomousAI
- [ ] Note: Momo HR will see it - doesn't matter, post anyway
- **TARGET AUDIENCE (STRICT REQUIREMENTS):**
  - Professional developers OR technical managers ONLY
  - Extremely deep domain knowledge in software engineering (NOT hobbyist coders)
  - Must have operated coding agents for 3+ months minimum
  - Ideally used Claude Code specifically for 2-3 months
  - BOTH conditions required - if not met, not target audience
- **WHY STRICT:** Software uses heavy processes, communication overhead, guardrails, gatekeeping to prevent hallucination. Consumes huge tokens. Not for hobbyists.
- **Priority**: P0 - Even without X, reaches recruiters/xAI team
- **Time**: 20 minutes
- **Note**: Demo video delegated to friend, post when video ready

### 4. README Finalization - 30 min
- [ ] **CRITICAL: Rewrite V6 README - Boss review says it's bad**
- [ ] **CRITICAL: Fix installation instructions for Claude MD**
- [ ] Boss concern: "If RMI is like this, I don't believe Claude can be installed and run"
- [ ] Use v5-README.md as base (but V6 needs major rewrite)
- [ ] Update with memory system details (after Component 2 complete)
- [ ] **Add target audience section** (professional devs with 3+ months Claude Code experience)
- [ ] Verify all installation instructions accurate and TESTABLE
- [ ] Copy to root as README.md when finalized
- **Priority**: P0 - Required for ship
- **Time**: 30 minutes → likely longer due to quality issues
- **Blocker**: Waiting for memory system completion
- **Boss feedback (2026-01-20)**: "V6 README overall pretty shitty. Installation file for Claude MD is shitty too."

---

## P1 - SHOULD DO (Required for MVP)

### Component 2: Memory System (IN PROGRESS)
- [x] **Sprint 1**: Test data + Qdrant infrastructure (COMPLETE)
- [x] **Sprint 2**: Voyage API + memory structure design (COMPLETE)
- [x] **Sprint 3**: Mini search engine (search, fetch, batch_fetch) - COMPLETE ✅
  - 3 reusable functions with TDD
  - 12/12 tests passing (100%)
  - Commit: cb96808
  - Two-stage retrieval validated
- [ ] **Sprint 4**: MCP server implementation - IN PROGRESS
  - DEV assigned to read mcp-builder skill and draft plan
  - Boss will review plan before implementation
  - TDD required
  - Wrap Sprint 3 functions (search, fetch, batch_fetch) as MCP tools
- [ ] Skills implementation (project-memory-store, project-memory-recall)
- [ ] Installation documentation
- [ ] **MCP Design**: Dynamic role/collection creation tool
  - Auto-create role collections if not found in Qdrant
  - Rarely used but needed for flexibility
  - Example: New role "qa" → auto-create "qa-patterns" collection
- **Status**: Boss + DEV + PO coordinating
- **Report to**: Boss AND PO@packaging-comandcenter when complete
- **NOTE**: Project-specific skills to avoid conflict with global coder-memory-* skills

### Component 3: Web UI - SQLite Conversion - 90 min
- [ ] Convert from PostgreSQL to SQLite for demo
- [ ] Hardcoded demo user: test/test123
- [ ] Update backend configuration
- [ ] Test installation
- [ ] Document SQLite setup
- **Priority**: P1 - Better UX, but optional if time tight
- **Time**: 90 minutes
- **Note**: Production uses PostgreSQL, demo uses SQLite

---

## P2 - NICE TO HAVE (Skip Unless Time Allows)

### Agent Team Value Proposition Document
- [ ] **DU: Write explanation of how agent teams work and why they're valuable**
- [ ] **Content areas**: See `docs/ideas/agent-team-value-proposition.md` for detailed ideas
- [ ] **Key topics**:
  - How multi-agent coordination works (tmux, tm-send, specialized roles)
  - Self-improvement via memory (agents learn from mistakes permanently)
  - Scrum adaptation (reality vs theory, execution-based not time-based)
  - Voice as thinking tool (not just typing replacement)
  - Progressive disclosure philosophy
- [ ] **Use cases**: Landing page, README intro, blog post, demo video context
- [ ] **Deliverable**: Organized document in `docs/` or integrate into README
- **Priority**: P2 - Post-ship documentation
- **Time**: TBD (content development)
- **Note**: Keep practical, focus on real problems solved

### Qdrant Docker Data Loss Issue - Research & Documentation
- [ ] **DU: Research Qdrant Docker data loss problem**
- [ ] **Problem**: Machine shutdown/Docker interruption causes memory loss
- [ ] **Suspected cause**: Docker RAM/buffer configuration
- [ ] **Research scope**:
  - Why Qdrant in Docker loses data on unexpected shutdown
  - Docker volume persistence configuration
  - Buffer/RAM settings that affect data durability
  - Best practices for preventing data loss
- [ ] **Deliverable**: Documentation in `docs/research/qdrant-docker-data-loss.md`
- [ ] **Action after research**: Implement fix in future sprint
- **Priority**: P2 - Important for production reliability
- **Time**: TBD (research phase)

### Demo Video - DELEGATED TO FRIEND
- [ ] Demo video production (30s technical demo)
- [ ] Script ready: 2 features (Scrum team + self-improving memory)
- [ ] **Status**: Delegated to friend
- [ ] **Reminder**: Call friend at 23:00 (11:00 PM) if not received yet
- **Priority**: P2 - Delegated, will be included in xAI email
- **Note**: Script and subtitles ready in `docs/demo-script/`

### Memory Generalization Research
- [ ] Research mechanism to generalize separate memory items into patterns
- [ ] **Problem**: Currently separate episodic memories don't combine into semantic patterns
- [ ] **Impact**: Individual memories isolated, no emergent general knowledge
- [ ] **Research needed**: How to detect patterns across multiple memories and create generalized semantic memories
- [ ] **Examples**:
  - Multiple JWT auth bugs → General "JWT token validation pattern"
  - Multiple React render issues → General "React rendering optimization pattern"
- **Priority**: P2 - Post-ship research (delivery tonight, can't research now)
- **Time**: TBD (research phase)
- **Note**: Current v7 spec stores memories but lacks auto-generalization mechanism

### Unlock X Account
- [ ] Contact X support to unlock suspended account
- [ ] Check for suspicious activity/spam
- [ ] Secure account (change password, 2FA)
- [ ] Once unlocked, post demo video there too
- **Priority**: P2 - Too complicated, not worth time tonight
- **Note**: X account locked (suspected hack/spam), Elon not on LinkedIn
- **Alternative**: LinkedIn + direct xAI email sufficient for tonight

### CLI: Project-Specific Scrum Team Creator
- [ ] Create CLI command to generate customized Scrum teams for user projects
- [ ] **Base Template**: Use tmux-team-creator + Scrum team template
- [ ] **Standard Roles**:
  - Product Owner (PO)
  - Scrum Master (SM)
  - Tech Lead (TL)
  - Backend Dev (BE)
  - Frontend Dev (FE)
  - QA Engineer (QA)
- [ ] **Project-Specific Customization**:
  - Detect project type (analyze codebase, ask user)
  - Add specialized roles based on project needs
  - Examples: AI Researcher (LLM projects), DevOps (cloud projects), Data Engineer (data projects)
- [ ] **Usage**: `create-scrum-team <project-path>` or similar
- [ ] **Implementation**: Interactive CLI prompts for customization
- **Priority**: P2 - Post-ship feature (after all core components done)
- **Time**: TBD (needs design review)
- **Note**: Details to be reviewed later, concept captured

### One-Command Init (npx create-tmux-team)
- **Status**: SKIP - Too complex for today
- **Reason**: Post-launch feature
- **Boss decision**: Not required for initial ship

### Chatbot on Web UI
- **Goal**: Popup chatbot to guide users
- **Status**: Skip - Not enough time
- **Priority**: P2 - Post-launch

### Boss Verification Tasks
- [ ] Verify tmux-team-creator.skill packaging
- [ ] Test install-tmux-skill.sh
- [ ] Verify all 5 templates work

---

## P3 - POST-LAUNCH

- [ ] PostgreSQL support documentation
- [ ] Docker-based installation option
- [ ] CI/CD pipeline for releases
- [ ] Automated testing for installers
- [ ] Advanced documentation
- [ ] Code cleanup and polish

---

## Critical Context

**Mission**: Ship as proof of work for job applications (xAI, Axon ASOM, international contracts)

**Constraints**:
- NO refactoring
- NO redesign
- NO improvements unless directly needed for shipping
- Ship raw truth, not perfect theory
- Proof beats pitch

**Time Pressure**: Must ship by 11:59 PM TODAY

**Coordination**:
- When memory system complete → Report to Boss AND `tm-send -s packaging-comandcenter PO "message"`
- packaging-comandcenter README blocked on memory system completion

---

## Notes

- **NEVER TOUCH**: Original project at `/home/hungson175/dev/coding-agents/AI-teams-controller`
- **WORK ON**: Public fork at `/home/hungson175/dev/coding-agents/AI-teams-controller-public`
- Code split across 3 projects: UI, Agent skills/prompts, Memory system
- Focus: Package existing code, clean sensitive data, create demo video

---

**Priority Framework**:
- **P0**: Blocker preventing ship → Must do today
- **P1**: Required for MVP → Do if time allows
- **P2**: Nice to have → Skip if time tight
- **P3**: Post-launch → After successful ship
