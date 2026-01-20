# Pre-Publishing Checklist - CRITICAL

**Complete ALL items below before public distribution**

## 1. API Keys Generated
- [ ] xAI key created and added to .env
- [ ] Soniox key created and added to .env
- [ ] Voyage AI key created and added to .env
- [ ] Google Cloud TTS service account created and JSON added
- [ ] OpenAI key created and added to .env
- [ ] All keys prefixed with "TO-BE-REMOVED" comments
- [ ] Provider console reminders set (delete after testing period)
- **See**: `backlog/api-keys-generation.md` for detailed requirements

## 2. Memory System Complete
- [ ] Sprint 4 MCP server implemented and tested
- [ ] Installation script created (fully automated)
- [ ] Documentation added to README
- [ ] Qdrant setup automated (Docker or standalone)
- [ ] Test: Fresh install on clean Docker should work immediately

## 3. README Finalized
- [ ] v6 README reviewed and rewritten (Boss: "V6 overall pretty shitty")
- [ ] Memory system section added
- [ ] Installation instructions tested and validated
- [ ] Target audience clearly stated
- [ ] All file paths verified

## 4. Sensitive Files Removed
- [ ] CLAUDE.md removed from project root
- [ ] Any .claude/ directories with sensitive info cleaned
- [ ] No personal data in committed files
- [ ] Check for hardcoded credentials

## 5. Installation Scripts
- [ ] tmux-team-creator skill installer works
- [ ] Memory system installer works (zero manual setup)
- [ ] Web UI installer works (SQLite demo mode)
- [ ] All scripts tested on clean environment

## 6. Demo Materials Ready
- [ ] Demo video received from friend (30s)
- [ ] Screenshots prepared
- [ ] LinkedIn post drafted

## 7. Final Testing
- [ ] Boss: Fresh Docker test (read README, Claude Code auto-installs)
- [ ] All 3 components install and run
- [ ] No manual configuration required
- [ ] Error handling graceful

## 8. GitHub Repository
- [ ] All commits pushed
- [ ] Repository set to public
- [ ] License added
- [ ] Contributing guidelines (if applicable)

**Status**: Template created - items to be checked off during execution
**Owner**: Team (coordinated by PO)
**Critical**: Nothing ships until ALL items checked
