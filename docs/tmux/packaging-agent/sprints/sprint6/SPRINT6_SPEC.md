# Sprint 6: Component 1 Upgrade + Component 3 SQLite Conversion

**Sprint Goal**: Complete packaging for Components 1 & 3

**Parallel Tracks**:
- Track A: Upgrade Component 1 packaging to match Memory System quality
- Track B: Convert Component 3 (Web UI) from PostgreSQL to SQLite

---

## Track A: Component 1 Packaging Upgrade

### Objective
Bring tmux-team-creator installer to same professional quality as Memory System

### Current State
- ✅ install-tmux-skill.sh exists (71 lines)
- ✅ Functional (installs skill successfully)
- ❌ Lower quality than Memory System (no colors, no verification, minimal error handling)

### Requirements

**Add to install-tmux-skill.sh**:

1. **Colored Output Functions**
   ```bash
   log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
   log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
   log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
   log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
   ```

2. **Professional Banner**
   ```bash
   print_banner() {
       echo "╔════════════════════════════════════════════════════════╗"
       echo "║     tmux Team Creator Skill Installation              ║"
       echo "╚════════════════════════════════════════════════════════╝"
   }
   ```

3. **Prerequisites Check**
   - Check unzip command exists
   - Check bash version (>= 4.0)
   - Check tmux installed (skill requires tmux)

4. **Installation Verification**
   ```bash
   verify_installation() {
       log_info "Verifying installation..."

       # Check skill directory exists
       if [ -d "$SKILL_DIR/tmux-team-creator" ]; then
           log_success "Skill verified (tmux-team-creator)"
       else
           log_error "Skill verification failed"
           return 1
       fi

       # Check tm-send executable
       if [ -x "$TM_SEND_PATH" ]; then
           log_success "tm-send verified (executable)"
       else
           log_error "tm-send verification failed"
           return 1
       fi

       log_success "Installation verification complete"
   }
   ```

5. **Enhanced Next Steps**
   ```bash
   print_next_steps() {
       echo ""
       echo "╔════════════════════════════════════════════════════════╗"
       echo "║           Installation Complete! ✓                    ║"
       echo "╚════════════════════════════════════════════════════════╝"
       echo ""
       echo "Next steps:"
       echo ""
       echo "1. Create a tmux team:"
       echo "   /tmux-team-creator"
       echo ""
       echo "2. Or ask Claude Code:"
       echo "   'Create a Scrum team for my project'"
       echo ""
       echo "Installed Components:"
       echo "  - Skill: tmux-team-creator"
       echo "  - Tool: tm-send (for agent communication)"
       echo "  - Templates: 5 team templates"
       echo ""
       echo "Documentation:"
       echo "  ~/.claude/skills/tmux-team-creator/SKILL.md"
       echo ""
   }
   ```

6. **Better Error Handling**
   - Check if skill file exists before unzip
   - Provide recovery instructions on error
   - Clear error messages

### Acceptance Criteria
- ✅ Colored output (4 log levels: info, success, warning, error)
- ✅ Professional banner
- ✅ Prerequisites check (unzip, bash, tmux)
- ✅ Installation verification (skill dir + tm-send executable)
- ✅ Enhanced next steps section
- ✅ Better error messages
- ✅ Matches Memory System quality level

---

## Track B: Component 3 SQLite Conversion

### Objective
Convert Web UI from PostgreSQL to SQLite for demo (hardcoded test/test123 user)

### Current State
**Database Schema** (2 tables):
1. **users**: email, username, hashed_password, is_active, timestamps, soft_delete
2. **user_settings**: voice detection settings (4 fields), UI preferences (1 field)

**Current Setup**: PostgreSQL + asyncpg driver

### Conversion Requirements

1. **Update database.py**
   ```python
   # OLD
   DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/aicontroller"

   # NEW
   DATABASE_URL = os.environ.get(
       "DATABASE_URL",
       "sqlite+aiosqlite:///./aicontroller.db"  # Local SQLite file
   )
   ```

2. **Update Dependencies**
   - Remove: asyncpg
   - Add: aiosqlite
   - Update requirements.txt

3. **Create Initial Data Script**
   ```python
   # scripts/init_sqlite_demo.py
   async def create_demo_user():
       """Create hardcoded test/test123 user with default settings."""
       # Create user: test / test123
       # Create default user_settings
   ```

4. **Update .env.example**
   ```bash
   # Database (SQLite for demo)
   DATABASE_URL=sqlite+aiosqlite:///./aicontroller.db

   # Remove PostgreSQL variables
   ```

5. **Test Migration**
   - Verify schema creates correctly
   - Verify test/test123 login works
   - Verify settings save/load works

### Files to Modify
- `backend/app/database.py` (DATABASE_URL)
- `backend/requirements.txt` (remove asyncpg, add aiosqlite)
- `backend/.env.example` (SQLite URL)
- Create: `backend/scripts/init_sqlite_demo.py`
- Update: Backend README with SQLite instructions

### Acceptance Criteria
- ✅ SQLite database file created on first run
- ✅ Schema creates correctly (users + user_settings tables)
- ✅ Hardcoded test/test123 user works
- ✅ Default voice settings work
- ✅ No PostgreSQL dependency
- ✅ Documentation updated

---

## Delivery Strategy

**Option 1**: Sequential (one after another)
- DEV completes Track A → Track B

**Option 2**: Parallel (both simultaneously)
- DEV works on both, alternating or in chunks

**Estimated Time**:
- Track A: 1-2 hours (packaging upgrade)
- Track B: 90 minutes (SQLite conversion)
- Total: 2.5-3.5 hours

---

## Testing Requirements

**Track A Testing**:
- Run install-tmux-skill.sh on clean system
- Verify colored output works
- Verify prerequisites check works
- Verify installation verification works
- Test error handling (missing unzip, etc.)

**Track B Testing**:
- Delete existing database
- Run backend with SQLite
- Verify schema creates
- Login with test/test123
- Update voice settings
- Verify settings persist

---

## Documentation Updates

**After Track A**:
- Update README Component 1 section (installation verified)

**After Track B**:
- Update README Component 3 section (SQLite demo mode)
- Update backend README with SQLite setup

---

**Sprint 6 Priority**: P0 (blocks public distribution)
**Both tracks required for MVP**
