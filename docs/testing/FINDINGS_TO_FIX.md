# Installation Test Findings - Master Tracker

**Test Date**: 2026-01-20
**Environment**: Fresh LXD Container (Ubuntu)
**Total Findings**: 10

---

## Status Summary

| Status | Count |
|--------|-------|
| ✅ FIXED | 6 |
| 🔄 IN PROGRESS | 2 |
| ❌ TODO | 2 |

---

## Findings Detail

### Finding #1: --dangerously-skip-permissions Flag Required
**Severity**: 🔴 CRITICAL
**Status**: ✅ FIXED
**Commit**: 646c566

**Issue**: Claude Code installation fails without --dangerously-skip-permissions flag.

**Fix Required**: README documentation

**Resolution**:
- Added flag to README installation step
- Code block shows exact command
- Warning added for visibility

---

### Finding #2: Root User Restriction
**Severity**: 🔴 CRITICAL
**Status**: ✅ FIXED
**Commit**: 953cf55

**Issue**: --dangerously-skip-permissions flag fails when running as root user.

**Impact**: Blocks installation in LXD/Docker containers, VMs (default root).

**Fix Required**: README documentation

**Resolution**:
- Added warning before installation steps
- Provided useradd and su commands
- Explained impact on containers/VMs

---

### Finding #3: Auth via Environment Variables (--settings flag)
**Severity**: 🔴 CRITICAL
**Status**: ✅ FIXED
**Commit**: 60a228f

**Issue**: Claude Code command incomplete - missing --settings flag.

**Fix Required**: README documentation

**Resolution**:
- Updated command to: `claude --settings ~/.claude/settings.json --dangerously-skip-permissions`
- Changed "flag" to "flags" (plural)

---

### Finding #4: sudo Access Requirement
**Severity**: 🟡 HIGH
**Status**: ✅ FIXED
**Commit**: 2d0b9c4

**Issue**: Installation scripts require sudo to install dependencies (unzip, etc).

**Impact**: Users without sudo cannot install on shared systems.

**Fix Required**: README documentation

**Resolution**:
- Added System Requirements section
- Documented sudo requirement
- Provided alternative: pre-install unzip, bash 4.0+

---

### Finding #5: PATH Configuration for tm-send
**Severity**: 🟡 HIGH
**Status**: ✅ FIXED
**Commit**: 056bab5

**Issue**: After installation, tm-send command not found if ~/.local/bin not in PATH.

**Fix Required**: README troubleshooting documentation

**Resolution**:
- Added Troubleshooting section to README
- Provided export PATH command
- Showed how to reload shell

**Future Enhancement**: Consider auto-adding to PATH in installer (DEV task)

---

### Finding #6: Docker Group Permission
**Severity**: 🟡 HIGH
**Status**: ❌ TODO
**Commit**: N/A

**Issue**: User needs to be in docker group to run Docker commands without sudo.

**Impact**: Memory system installation fails (Qdrant requires Docker).

**Fix Required**: README documentation

**Action Needed**:
- Add to System Requirements section
- Provide usermod command to add user to docker group
- Explain need to log out/in for group to take effect

**Suggested Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in for group to take effect
```

---

### Finding #7: PEP 668 Virtual Environment Requirement
**Severity**: 🟡 HIGH
**Status**: 🔄 IN PROGRESS (DEV fixing)
**Commit**: N/A

**Issue**: Modern Python distributions (PEP 668) require venv for pip install.

**Impact**: Memory system installation fails with "externally-managed-environment" error.

**Fix Required**: Installation script update

**Action Needed** (DEV):
- Modify install-memory-system.sh to always use venv
- Ensure venv activation before pip install
- Update script to create venv if not exists

---

### Finding #8: Backend pyproject.toml Flat-Layout Issue
**Severity**: 🟡 HIGH
**Status**: 🔄 IN PROGRESS (DEV fixing)
**Commit**: N/A

**Issue**: Backend pyproject.toml uses flat-layout but directory structure is src-layout.

**Impact**: pip install fails with "directory 'app' does not exist" error.

**Fix Required**: Backend restructure or pyproject.toml update

**Action Needed** (DEV):
- Either: Restructure backend to flat-layout (move app/ to root)
- Or: Update pyproject.toml to src-layout configuration
- Test pip install -e . works correctly

---

### Finding #9: Frontend Missing @codemirror/lang-yaml Dependency
**Severity**: 🟢 MEDIUM
**Status**: ✅ FIXED (DEV completed, needs commit)
**Commit**: Pending DEV commit

**Issue**: Frontend package.json missing @codemirror/lang-yaml dependency.

**Impact**: Frontend build fails with "Cannot find module" error.

**Fix Required**: package.json update

**Resolution** (DEV):
- Added @codemirror/lang-yaml to package.json dependencies
- Frontend now builds successfully
- Waiting for DEV commit

---

### Finding #10: /init-role Command Missing
**Severity**: 🔴 CRITICAL
**Status**: ❌ TODO
**Commit**: N/A

**Issue**: /init-role command referenced in documentation but command file does not exist.

**Impact**: Users trying to use /init-role command get "command not found" error.

**Fix Required**: Create command file OR remove references

**Action Needed**:
Option A: Create /init-role command at ~/.claude/commands/init-role.md
Option B: Remove all references to /init-role from documentation
Option C: Replace with alternative initialization method

**Boss Decision Required**: Which option to pursue?

---

## Priority Summary

### 🔴 CRITICAL (Need Immediate Action)
- Finding #10: /init-role command missing → **UNFIXED**

### 🟡 HIGH (Should Fix Soon)
- Finding #6: Docker group permission → **TODO (README)**
- Finding #7: PEP 668 venv requirement → **IN PROGRESS (DEV)**
- Finding #8: pyproject.toml flat-layout → **IN PROGRESS (DEV)**

### 🟢 MEDIUM (Minor Issues)
- Finding #9: Frontend dependency → **FIXED (pending commit)**

---

## Next Actions

### DU (Document Updater) - Immediate
1. Add Finding #6 to README (Docker group permission)
2. Update INSTALLATION_TEST_REPORT.md when all findings resolved

### DEV (Developer) - In Progress
1. Complete Finding #7 fix (PEP 668 venv script update)
2. Complete Finding #8 fix (pyproject.toml or restructure)
3. Commit Finding #9 fix (frontend dependency)

### Boss Decision Required
1. Finding #10: Create /init-role command OR remove references?

---

## Tracking Notes

**Last Updated**: 2026-01-20 00:17
**Next Review**: After DEV completes in-progress items
**Target**: All findings resolved before public release

---

**Maintained By**: DU (Document Updater)
**Source**: DEV's comprehensive installation test (Phases 1-6)
