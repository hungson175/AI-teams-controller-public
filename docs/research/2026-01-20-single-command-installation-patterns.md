# Single Command Installation Research

**Date**: 2026-01-20
**Researcher**: DEV
**Topic**: Installation patterns for multi-component self-hosted applications

---

## Executive Summary

Researched installation patterns for self-hosted applications with multiple components (frontend, backend, database, services). Examined 10+ popular open-source projects to identify best practices for single-command installation.

**Key Finding**: Two dominant patterns emerge:
1. **curl | bash** - Single script that handles everything (Coolify: 49k stars)
2. **bash script + Docker Compose** - Script sets up configuration, then launches containers (Sentry, Jitsi)

**Recommendation**: Hybrid approach combining both patterns is optimal for AI Teams Controller.

---

## Research Methodology

### 1. Projects Examined

| Project | Stars | Tech Stack | Installation Pattern |
|---------|-------|------------|---------------------|
| [n8n](https://github.com/n8n-io/n8n) | 170k | Node.js, TypeScript | Docker single command |
| [Supabase](https://github.com/supabase/supabase) | 96k | Postgres, Elixir, Go | Docker Compose |
| [Coolify](https://github.com/coollabsio/coolify) | 49k | PHP, Docker | curl \| bash installer |
| [Mastodon](https://github.com/mastodon/mastodon) | 49k | Ruby, Rails, Postgres, Redis | Docker Compose |
| [Discourse](https://github.com/discourse/discourse) | 46k | Ruby, Rails, Ember.js | Docker launcher script |
| [Appwrite](https://github.com/appwrite/appwrite) | 54k | Multiple services | Docker Compose |
| [ERPNext](https://github.com/frappe/erpnext) | 31k | Python, MariaDB | Frappe Bench (custom) |
| [GitLab](https://github.com/gitlabhq/gitlabhq) | 24k | Ruby, Go, Postgres | Omnibus installer |
| [Plausible CE](https://github.com/plausible/community-edition) | 2k | Elixir, ClickHouse | Manual Docker Compose |
| [awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted) | 269k | N/A | Curated list (reference) |

### 2. Data Sources

- GitHub repository READMEs and installation documentation
- Web search for installation patterns and best practices (2024-2026)
- Bash scripting best practices from multiple sources

---

## Installation Pattern Categories

### Pattern 1: Single curl | bash Command

**Example: Coolify**

```bash
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash
```

**How It Works:**
- Downloads and executes installation script in one step
- Script handles dependency checking (curl, wget, git, jq, openssl)
- Installs all components automatically
- Supports multiple Linux distributions (Debian, Ubuntu, CentOS, Fedora, Arch, Alpine, SLES)

**Pros:**
- ✅ Simplest user experience (one command)
- ✅ No manual configuration required
- ✅ Fast onboarding for new users
- ✅ Easy to communicate ("just run this command")

**Cons:**
- ❌ Less transparency (users can't easily review script first)
- ❌ Requires internet connection during installation
- ❌ Security concerns (running remote scripts as root)
- ❌ Harder to customize installation

**Source**: [Coolify Installation](https://coolify.io/docs/get-started/installation)

---

### Pattern 2: Git Clone + bash Script + Docker Compose

**Example: Sentry**

```bash
git clone https://github.com/getsentry/self-hosted.git
cd self-hosted
./install.sh
docker compose up --wait
```

**How It Works:**
1. Clone repository with all configuration files
2. Run install script that:
   - Checks dependencies
   - Generates secrets/passwords
   - Modifies .env file automatically
   - Sets up initial configuration
3. Launch services with Docker Compose

**Password Generation Pattern** (from Jitsi):
```bash
./gen-passwords.sh  # Uses openssl rand -hex 16
```

**Pros:**
- ✅ Transparent (users can review code before running)
- ✅ Easy to customize (modify .env before launching)
- ✅ Works offline after initial clone
- ✅ Reproducible installations
- ✅ Git history for troubleshooting

**Cons:**
- ❌ Multiple steps required
- ❌ Users need to understand Git
- ❌ More complex initial setup

**Sources**:
- [Sentry Self-Hosted](https://develop.sentry.dev/self-hosted/)
- [Jitsi Docker Guide](https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-docker/)

---

### Pattern 3: Manual Docker Compose Setup

**Example: Plausible Community Edition**

**Steps:**
1. Clone repository
2. Manually configure `.env` file (BASE_URL, SECRET_KEY_BASE)
3. Create `docker-compose.override.yml` for port exposure
4. Run `docker compose up -d`
5. Access web interface and create first user

**Pros:**
- ✅ Maximum flexibility
- ✅ Complete control over configuration
- ✅ Easy to understand for experienced users

**Cons:**
- ❌ High friction for beginners
- ❌ Error-prone (manual configuration mistakes)
- ❌ Not truly "single command"
- ❌ Requires Docker/Docker Compose knowledge

**Source**: [Plausible Community Edition](https://github.com/plausible/community-edition)

---

### Pattern 4: Custom Installer Tools

**Example: Frappe Bench (ERPNext)**

Custom Python-based installer that manages:
- Multiple sites on same server
- Virtual environments
- Database configuration
- Service management

**Pros:**
- ✅ Tailored to specific ecosystem needs
- ✅ Advanced management features
- ✅ Multi-site support

**Cons:**
- ❌ Steep learning curve
- ❌ Additional tool to maintain
- ❌ Not portable to other projects

---

## Docker Compose Best Practices

Based on research from multiple self-hosted projects:

### 1. Environment Variables

**Standard Pattern:**
- Configuration via `.env` file (not editing docker-compose.yml)
- Docker Compose automatically reads `.env` in same directory
- Variables available during build AND runtime

**Example .env structure:**
```bash
# Base Configuration
BASE_URL=http://localhost:3337
SECRET_KEY_BASE=<generated-64-char-secret>

# Database
DATABASE_URL=sqlite+aiosqlite:///./aicontroller.db

# API Keys
SONIOX_API_KEY=<your-key>
XAI_API_KEY=<your-key>
```

### 2. Storage with Relative Paths

**Recommended:**
```yaml
volumes:
  - ./data:/app/data
  - ./logs:/app/logs
```

**Why:** Portable, simple, keeps data with project

**Avoid:**
- Named volumes (harder to find data)
- Absolute paths (not portable)

**Source**: [Docker Self-Hosting Guide](https://github.com/DoTheEvo/selfhosted-apps-docker)

### 3. Service Dependencies

```yaml
services:
  backend:
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
```

**Source**: [Docker Compose Multi-Container](https://docs.docker.com/get-started/docker-concepts/running-containers/multi-container-applications/)

---

## Bash Script Best Practices

Research findings from Linux Bash resources:

### 1. Dependency Checking

**Pattern:**
```bash
check_dependencies() {
    local deps=("docker" "docker-compose" "git" "curl")
    local missing=()

    for cmd in "${deps[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -ne 0 ]; then
        echo "Missing dependencies: ${missing[*]}"
        exit 3  # Specific exit code for missing deps
    fi
}
```

**Key Points:**
- Use `command -v` (POSIX-compliant)
- Validate early, fail fast
- Collect all missing deps before failing
- Use specific exit codes

**Sources**:
- [Dependency Checking in Scripts](https://www.linuxbash.sh/post/installing-software-and-managing-dependencies-in-scripts)
- [Program Existence Validation](https://www.codestudy.net/blog/how-can-i-check-if-a-program-exists-from-a-bash-script/)

### 2. Error Handling

**Essential Commands:**
```bash
set -e  # Exit on error
set -u  # Exit on undefined variable
set -o pipefail  # Catch errors in pipes
```

**Exit Code Strategy:**
```bash
EXIT_SUCCESS=0
EXIT_CONFIG_ERROR=2
EXIT_DEPENDENCY_ERROR=3
EXIT_PERMISSION_ERROR=4
EXIT_NETWORK_ERROR=5
```

**Cleanup with Trap:**
```bash
cleanup() {
    echo "Cleaning up..."
    rm -f /tmp/install-$$.*
}

trap cleanup EXIT
```

**Sources**:
- [Error Handling Best Practices](https://moldstud.com/articles/p-best-practices-and-techniques-for-error-handling-in-bash-scripts)
- [Error Handling in 2025](https://dev.to/rociogarciavf/how-to-handle-errors-in-bash-scripts-in-2025-3bo)

### 3. Idempotency

**Pattern:**
```bash
install_component() {
    if [ -d "$INSTALL_DIR/component" ]; then
        echo "Component already installed, updating..."
        rm -rf "$INSTALL_DIR/component"
    fi
    cp -r component "$INSTALL_DIR/"
}
```

**Why:** Users can re-run installer safely without breaking existing setup

### 4. Informative Output

**Color Coding:**
```bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
```

**Progress Indicators:**
```bash
echo "Installing components..."
echo "  [1/5] Checking dependencies..."
echo "  [2/5] Setting up database..."
```

**Source**: [Bash Script Best Practices](https://bashscript.net/bash-script-best-practices/)

### 5. User Prompts and Defaults

**Pattern:**
```bash
read -p "Install directory [/opt/ai-teams-controller]: " INSTALL_DIR
INSTALL_DIR=${INSTALL_DIR:-/opt/ai-teams-controller}
```

**For Secrets:**
```bash
if [ -z "$SECRET_KEY" ]; then
    SECRET_KEY=$(openssl rand -hex 32)
    echo "Generated SECRET_KEY: $SECRET_KEY"
fi
```

---

## Orchestration Patterns for Multi-Component Apps

### Standard Components:
1. **Frontend** (Next.js on port 3337)
2. **Backend** (FastAPI on port 17063)
3. **Terminal Service** (Node.js on port 17073)
4. **Database** (SQLite - file-based, or optional Postgres)
5. **Additional Services** (Redis, Celery workers)

### Docker Compose Structure:

```yaml
version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3337:3337"
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://localhost:17063
    depends_on:
      - backend

  backend:
    build: ./backend
    ports:
      - "17063:17063"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    volumes:
      - ./data:/app/data
    depends_on:
      db:
        condition: service_healthy

  terminal:
    build: ./terminal
    ports:
      - "17073:17073"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=ai_teams
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - ./db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 5s
      timeout: 5s
      retries: 5
```

**Sources**:
- [Multi-Container Applications](https://dev.to/techwithhari/docker-compose-orchestrating-multi-container-applications-1n7b)
- [Frontend Backend DB Example](https://wkrzywiec.medium.com/how-to-run-database-backend-and-frontend-in-a-single-click-with-docker-compose-4bcda66f6de)

---

## Recommendations for AI Teams Controller

### Recommended Approach: Hybrid Pattern

Combine the best of both worlds:

**Option A: Single Install Script (Recommended)**
```bash
# For users who want simplicity
curl -fsSL https://raw.githubusercontent.com/user/repo/main/install.sh | bash
```

**Option B: Git Clone Method (For developers)**
```bash
# For users who want control
git clone https://github.com/user/ai-teams-controller.git
cd ai-teams-controller
./install.sh
```

### Installer Script Structure

```
install.sh
├── 1. Check prerequisites
│   ├── Docker
│   ├── Docker Compose
│   ├── Git (if git clone method)
│   └── curl/wget
│
├── 2. Detect installation mode
│   ├── Fresh install
│   └── Update existing installation
│
├── 3. Component installation
│   ├── Component 1: tmux Team Creator Skill
│   │   ├── Copy to ~/.claude/skills/
│   │   └── Install tm-send to ~/.local/bin/
│   │
│   ├── Component 2: Memory System
│   │   ├── Start Qdrant (Docker)
│   │   ├── Install MCP server
│   │   ├── Install skills (coder-memory-store, coder-memory-recall)
│   │   ├── Install subagent (memory-only)
│   │   └── Install hooks
│   │
│   └── Component 3: Web UI
│       ├── Generate secrets (.env)
│       ├── Setup frontend (Next.js)
│       ├── Setup backend (FastAPI)
│       ├── Initialize database
│       └── Create demo user
│
├── 4. Configuration
│   ├── Generate .env if missing
│   ├── Generate secrets (JWT, API keys)
│   └── Set default ports
│
├── 5. Launch services
│   ├── Docker Compose up -d
│   └── Wait for health checks
│
└── 6. Post-install
    ├── Display status
    ├── Show demo credentials
    ├── Print next steps
    └── Show URLs
```

### Installation Script Template

```bash
#!/bin/bash
set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Exit codes
EXIT_SUCCESS=0
EXIT_DEPENDENCY_ERROR=3
EXIT_CONFIG_ERROR=2

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Cleanup on exit
cleanup() {
    log_info "Cleaning up..."
}
trap cleanup EXIT

# Check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    local deps=("docker" "docker-compose")
    local missing=()

    for cmd in "${deps[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            missing+=("$cmd")
        fi
    done

    if [ ${#missing[@]} -ne 0 ]; then
        log_error "Missing dependencies: ${missing[*]}"
        log_info "Please install: ${missing[*]}"
        exit $EXIT_DEPENDENCY_ERROR
    fi

    log_success "All dependencies found"
}

# Generate secrets
generate_secrets() {
    if [ -z "${JWT_SECRET_KEY:-}" ]; then
        JWT_SECRET_KEY=$(openssl rand -hex 32)
        log_success "Generated JWT_SECRET_KEY"
    fi
}

# Install Component 1: tmux Team Creator
install_tmux_skill() {
    log_info "[1/3] Installing tmux Team Creator Skill..."
    # Implementation here
    log_success "tmux Team Creator installed"
}

# Install Component 2: Memory System
install_memory_system() {
    log_info "[2/3] Installing Memory System..."
    # Implementation here
    log_success "Memory System installed"
}

# Install Component 3: Web UI
install_web_ui() {
    log_info "[3/3] Installing Web UI..."

    # Generate .env
    cat > .env <<EOF
DATABASE_URL=sqlite+aiosqlite:///./aicontroller.db
JWT_SECRET_KEY=${JWT_SECRET_KEY}
SONIOX_API_KEY=${SONIOX_API_KEY:-}
XAI_API_KEY=${XAI_API_KEY:-}
EOF

    # Start services
    docker-compose up -d --wait

    log_success "Web UI installed"
}

# Display next steps
show_next_steps() {
    echo ""
    echo "╔════════════════════════════════════════════════╗"
    echo "║     Installation Complete! ✓                  ║"
    echo "╚════════════════════════════════════════════════╝"
    echo ""
    log_success "Frontend: http://localhost:3337"
    log_success "Backend:  http://localhost:17063"
    log_success "Terminal: http://localhost:17073"
    echo ""
    log_info "Demo credentials:"
    echo "  Email:    test@example.com"
    echo "  Password: test123"
    echo ""
}

# Main installation flow
main() {
    echo "╔════════════════════════════════════════════════╗"
    echo "║   AI Teams Controller Installation             ║"
    echo "╚════════════════════════════════════════════════╝"
    echo ""

    check_dependencies
    generate_secrets

    install_tmux_skill
    install_memory_system
    install_web_ui

    show_next_steps
}

main "$@"
```

---

## Key Considerations for AI Teams Controller

### 1. Component Independence

Each component should be independently installable:
- `./install-tmux-skill.sh` (standalone)
- `./install-memory-system.sh` (standalone)
- `./install-web-ui.sh` (standalone)
- `./install-all.sh` (orchestrates all three)

**Benefit:** Users can install only what they need

### 2. Progressive Installation

For users with different needs:
- **Minimal**: Just tmux skill (no Docker required)
- **Standard**: Tmux skill + Memory system
- **Complete**: All three components

### 3. Update Strategy

Script should detect existing installations:
```bash
if [ -d "$HOME/.claude/skills/coder-memory-store" ]; then
    log_info "Memory skills already installed, updating..."
    # Update logic
fi
```

### 4. Configuration Management

- Generate secrets automatically (secure defaults)
- Allow users to provide their own values
- Never commit secrets to git
- Provide `.env.example` template

### 5. Platform Support

Test on:
- Ubuntu 22.04+ (primary target)
- Debian 11+
- macOS (limited Docker support)

---

## Resources

### Curated Lists
- [awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted) (269k stars)
- [awesome-selfhost-docker](https://github.com/hotheadhacker/awesome-selfhost-docker)
- [Awesome Docker Compose](https://awesome-docker-compose.com/)

### Documentation Sources
- [Coolify Installation](https://coolify.io/docs/get-started/installation)
- [Sentry Self-Hosted](https://develop.sentry.dev/self-hosted/)
- [Supabase Docker Self-Hosting](https://supabase.com/docs/guides/self-hosting/docker)
- [Jitsu Docker Guide](https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-docker/)
- [Docker Compose Multi-Container Apps](https://docs.docker.com/get-started/docker-concepts/running-containers/multi-container-applications/)

### Best Practices
- [Installing Software in Scripts](https://www.linuxbash.sh/post/installing-software-and-managing-dependencies-in-scripts)
- [Automating Software Deployment](https://www.linuxbash.sh/post/automating-software-deployment-with-bash-scripts)
- [Error Handling in Bash](https://moldstud.com/articles/p-best-practices-and-techniques-for-error-handling-in-bash-scripts)
- [Bash Script Best Practices](https://bashscript.net/bash-script-best-practices/)
- [Program Existence Validation](https://www.codestudy.net/blog/how-can-i-check-if-a-program-exists-from-a-bash-script/)

### Example Projects
- [Coolify](https://github.com/coollabsio/coolify) - curl | bash installer
- [n8n](https://github.com/n8n-io/n8n) - Docker single command
- [Discourse](https://github.com/discourse/discourse) - Docker launcher
- [Plausible CE](https://github.com/plausible/community-edition) - Docker Compose
- [Fullstack Docker Project](https://github.com/faysalmehedi/fullstack-docker-project) - Frontend + Backend + DB example
- [Docker Frontend Backend DB](https://github.com/knaopel/docker-frontend-backend-db) - Multi-container sample

---

## Next Steps

1. **Review this research** with PO and Boss
2. **Design unified installer** architecture
3. **Implement install-all.sh** that orchestrates:
   - Component 1: tmux Team Creator (existing)
   - Component 2: Memory System (existing)
   - Component 3: Web UI (needs Docker Compose setup)
4. **Test on clean Ubuntu 22.04** VM
5. **Document installation** for users
6. **Create uninstall script** (good practice)

---

**Research Complete**: 2026-01-20 15:40
