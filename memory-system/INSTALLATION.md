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
