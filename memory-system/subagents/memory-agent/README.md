# Memory Agent

A specialized Claude Code subagent for memory operations with the vector database.

## Purpose

The memory-agent is designed to interact ONLY with the Qdrant vector database via MCP memory tools. It has **zero access** to file system tools (Read, Write, Edit, Glob, Bash) to prevent context pollution.

## Usage

This agent is automatically invoked by the memory skills:
- `project-memory-store` - Stores coding patterns and lessons
- `project-memory-recall` - Retrieves relevant memories

You typically don't invoke this agent directly - the skills handle that for you.

## Installation

The installation script (`install-memory-system.sh`) automatically installs this agent to `~/.claude/agents/memory-agent.md`.

## How It Works

When a skill like `project-memory-store` runs, it uses:
```
Task tool with subagent_type: "memory-agent"
```

This spawns a separate agent context with:
- **Model**: Claude Haiku (fast and cost-effective)
- **Tools**: Only 7 MCP memory tools
- **Constraints**: No file system access
- **Color**: Blue (for visual identification)

## Design Rationale

**Why separate agent?**
- Prevents context pollution from file reads
- Isolates memory operations
- Keeps main agent focused on coding tasks
- More cost-effective (uses Haiku instead of Sonnet)

**Why no file access?**
- Early testing showed agents would read hundreds of files instead of using memory tools
- Tool restriction enforces correct behavior
- Clean separation of concerns

## Memory Collections

The agent works with role-based collections:
- `universal-patterns` - Cross-domain patterns
- `backend-patterns` - Backend/API patterns
- `frontend-patterns` - UI/React patterns
- `ai-patterns` - ML/AI patterns
- `devops-patterns` - Infrastructure patterns
- And more...

## Metadata Structure

All memories use this metadata format:
```json
{
  "memory_type": "episodic|procedural|semantic",
  "role": "backend|frontend|...",
  "title": "Plain text title",
  "description": "2-3 sentence summary",
  "tags": ["#tag1", "#tag2"],
  "confidence": "high|medium|low",
  "frequency": 1
}
```

## Verification

After installation, verify the agent is available:
```bash
ls ~/.claude/agents/memory-agent.md
```

## Troubleshooting

**"memory-agent not found"**
- Run installation script: `./install-memory-system.sh`
- Or manually copy: `cp subagents/memory-agent/memory-agent.md ~/.claude/agents/`

**"Cannot access file tools"**
- This is expected and by design
- Agent should only use MCP memory tools

## Related Files

- **Skills**: `~/.claude/skills/project-memory-{store,recall}/`
- **MCP Server**: Configured in `~/.claude/mcp.json` (or similar)
- **Hooks**: `~/.claude/hooks/memory_*.py` (automation)
