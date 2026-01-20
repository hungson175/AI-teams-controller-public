# Memory System Installation Guide

## Quick Start (Automated Installation)

**One command to install everything:**

```bash
./install-memory-system.sh
```

The script will:
1. ✓ Check prerequisites (Python 3.10+, pip, Docker)
2. ✓ Install Qdrant vector database (via Docker)
3. ✓ Install Python dependencies (in virtual environment)
4. ✓ Configure environment variables
5. ✓ Verify installation works

**Time**: 3-5 minutes on first run

---

## Prerequisites

### Required
- **Python 3.10+** - Core runtime
- **pip** - Python package manager

### Optional (Highly Recommended)
- **Docker** - For Qdrant installation (easiest method)
  - If Docker unavailable, manual Qdrant setup required

---

## Installation Process

### Step 1: Run Installer

```bash
cd memory-system
./install-memory-system.sh
```

The script runs interactively and will:
- Show progress with colored output
- Prompt for Voyage API key if not in .env
- Handle errors gracefully with clear messages

### Step 2: Activate Environment

```bash
source .venv/bin/activate
```

### Step 3: Verify Installation

Check that services are running:

```bash
# Test Qdrant
curl http://localhost:16333

# Test MCP server (if configured)
python -m src.mcp_server.server
```

---

## What Gets Installed

### 1. Qdrant Vector Database
- **Docker container**: `memory-system-qdrant`
- **Port**: 16333 (non-standard to avoid conflicts)
- **Data**: Stored in `./qdrant_storage/`
- **Version**: Latest from Docker Hub

### 2. Python Dependencies
- **Location**: `.venv/` (virtual environment)
- **Packages**:
  - qdrant-client >= 1.7.0
  - voyageai >= 0.2.0
  - mcp >= 1.0.0
  - pydantic >= 2.0.0
  - pytest (for testing)

### 3. Environment Configuration
- **File**: `.env`
- **Created from**: `.env.example`
- **Required**:
  - VOYAGE_API_KEY (for embeddings)
  - QDRANT_URL (auto-configured)

### 4. Memory Skills
- **project-memory-store**: Stores coding patterns automatically after task completion
- **project-memory-recall**: Retrieves relevant memories before complex tasks
- **Location**: `~/.claude/skills/`
- **Automatic triggering**: Via hooks (see Hooks section)

### 5. Memory Subagent
- **memory-agent**: Specialized agent for memory operations only
- **Tools**: MCP memory tools (search, store, get, list_collections)
- **Zero file access**: Cannot read/write/edit files (security)
- **Used by**: Memory skills for storage/retrieval operations

### 6. Memory Hooks
- **memory_store_reminder.py**: 33% probability reminder after task completion (Stop hook)
- **todowrite_memory_recall.py**: Triggers memory recall on first TodoWrite
- **Location**: `~/.claude/hooks/`
- **Purpose**: Automatic memory integration without manual skill invocation

---

## Configuration

### Voyage API Key

The installer will prompt for your Voyage AI API key if not found in `.env`.

**Get your key**: https://www.voyageai.com/

**Manual configuration**:
```bash
# Edit .env
VOYAGE_API_KEY=your-actual-key-here
```

### Custom Qdrant Port

Default: 16333

To change:
```bash
# Edit .env
QDRANT_URL=http://localhost:YOUR_PORT
```

---

## Running the MCP Server

After installation:

```bash
# Activate virtual environment
source .venv/bin/activate

# Run MCP server (stdio transport)
python -m src.mcp_server.server
```

**Claude Code Configuration**:
Add to `~/.claude/mcp.json`:
```json
{
  "mcpServers": {
    "memory": {
      "command": "python",
      "args": ["-m", "src.mcp_server.server"],
      "cwd": "/path/to/memory-system",
      "env": {
        "PYTHONPATH": "/path/to/memory-system"
      }
    }
  }
}
```

---

## Memory Skills

Memory skills provide automatic storage and retrieval of coding patterns without manual invocation.

### project-memory-store

**Purpose**: Store coding patterns, solutions, and lessons automatically after task completion

**Triggering**: Via `memory_store_reminder.py` hook (33% probability after tasks)

**What it stores**:
- Bug fixes and solutions
- Error patterns and resolutions
- Design decisions and trade-offs
- Coding patterns that worked well

**Usage**: Automatic - no manual invocation needed. Hook prompts to store when valuable lessons emerge.

### project-memory-recall

**Purpose**: Retrieve relevant memories before complex tasks

**Triggering**: Via `todowrite_memory_recall.py` hook (on first TodoWrite in session)

**What it recalls**:
- Similar problems solved before
- Relevant coding patterns
- Past lessons from related tasks

**Usage**: Automatic - triggered when you start planning complex tasks with TodoWrite.

**Manual invocation** (if needed):
```bash
# In Claude Code
/project-memory-recall
```

---

## Memory Subagent

The memory-agent is a specialized subagent dedicated to memory operations only.

### Purpose

Handles all memory storage and retrieval operations for memory skills. Isolated from file system for security.

### Capabilities

**Has access to**:
- MCP memory tools (search_memory, store_memory, get_memory, list_collections)
- Memory search and retrieval logic

**Does NOT have access to**:
- File read/write/edit tools
- Bash commands
- Any file system operations

### Why Isolated?

Security and specialization:
- Memory operations require different permissions than code editing
- Prevents accidental file modifications during memory operations
- Focuses solely on memory tasks without distractions

### Usage

Memory skills automatically spawn the memory-agent when needed. You don't interact with it directly.

**Example workflow**:
1. You complete a difficult task
2. `memory_store_reminder.py` hook prompts (33% chance)
3. You invoke `/project-memory-store`
4. Skill spawns memory-agent to handle storage
5. Memory-agent searches/stores via MCP tools
6. Done

---

## Hooks

Hooks automate memory integration without requiring manual skill invocation.

### memory_store_reminder.py

**Type**: Stop hook (runs after task completion)

**Trigger**: 33% probability after any task

**Purpose**: Remind you to store valuable lessons without being annoying

**Prompt**:
```
Check if any hard-earned lessons or failure patterns warrant storage.
Be EXTREMELY selective. If storing: store and report in 1 line.
If not: say 'Nothing worth storing.' and move on.
```

**Why 33%?**: Balance between capturing important lessons and not interrupting flow.

**Location**: `~/.claude/hooks/memory_store_reminder.py`

### todowrite_memory_recall.py

**Type**: PreToolUse hook (runs before TodoWrite tool)

**Trigger**: First TodoWrite in session (complex task planning detected)

**Purpose**: Automatically recall relevant memories when starting complex work

**Behavior**:
- Detects first TodoWrite (planning phase)
- Spawns memory-agent to search for relevant memories
- Presents findings before you start planning
- Subsequent TodoWrites don't trigger (only first one)

**Location**: `~/.claude/hooks/todowrite_memory_recall.py`

### Hook Configuration

Hooks are installed automatically by `install-memory-system.sh` to `~/.claude/hooks/`.

**Manual installation** (if needed):
```bash
# Copy hooks
cp hooks/*.py ~/.claude/hooks/

# Verify
ls ~/.claude/hooks/ | grep memory
```

---

## Verification

### Test Qdrant Connection

```bash
source .venv/bin/activate
python3 -c "
from qdrant_client import QdrantClient
client = QdrantClient(url='http://localhost:16333')
print('Collections:', [c.name for c in client.get_collections().collections])
"
```

### Test Voyage API

```bash
source .venv/bin/activate
python3 -c "
import voyageai
import os
from dotenv import load_dotenv
load_dotenv()
vo = voyageai.Client(api_key=os.getenv('VOYAGE_API_KEY'))
result = vo.embed(texts=['test'], model='voyage-4-lite')
print('Embedding dimension:', len(result.embeddings[0]))
"
```

Expected: `Embedding dimension: 1024`

---

## Troubleshooting

### Installation Fails

**"Docker not available"**
- Install Docker: https://docs.docker.com/get-docker/
- Or manually install Qdrant: https://qdrant.tech/documentation/quick-start/

**"Python version too old"**
- Install Python 3.10+: https://www.python.org/downloads/

**"Qdrant connection failed"**
- Check Docker container: `docker ps | grep qdrant`
- Check logs: `docker logs memory-system-qdrant`
- Restart: `docker restart memory-system-qdrant`

### Runtime Issues

**"Voyage API connection failed"**
- Verify API key in `.env`
- Check key validity: https://www.voyageai.com/
- Check rate limits

**"Collection not found"**
- Collections created on first use
- Or manually: See MCP tools documentation

---

## Uninstallation

### Remove Qdrant Container

```bash
docker stop memory-system-qdrant
docker rm memory-system-qdrant
```

### Remove Data

```bash
rm -rf qdrant_storage/
```

### Remove Virtual Environment

```bash
rm -rf .venv/
```

---

## Re-running Installation

The installer is **idempotent** - safe to run multiple times:
- Existing Qdrant container will be reused
- Existing .env will not be overwritten
- Dependencies will be updated if needed

```bash
./install-memory-system.sh
```

---

## Manual Installation (Advanced)

If you prefer manual setup:

### 1. Install Qdrant

```bash
docker run -d \
  --name memory-system-qdrant \
  -p 16333:6333 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant:latest
```

### 2. Install Python Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Voyage API key
```

### 4. Verify

```bash
python -m pytest tests/ -v
```

---

## Support

For issues or questions:
- Check troubleshooting section above
- Review logs: `docker logs memory-system-qdrant`
- File issue: [GitHub Issues](https://github.com/your-repo/issues)

---

**Installation Time**: 3-5 minutes (first run)
**Disk Space**: ~500MB (Docker image + dependencies)
**Memory**: ~512MB (Qdrant runtime)
