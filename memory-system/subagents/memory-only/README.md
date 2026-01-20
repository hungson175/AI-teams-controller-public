# Memory-Only Agent

A specialized Claude Code subagent for memory operations with the vector database.

## Purpose

The memory-only is designed to interact ONLY with the Qdrant vector database via MCP memory tools. It has **zero access** to file system tools (Read, Write, Edit, Glob, Bash) to prevent context pollution.

## Usage

This agent is automatically invoked by the memory skills:
- `memory-store` - Stores coding patterns and lessons
- `memory-recall` - Retrieves relevant memories

You typically don't invoke this agent directly - the skills handle that for you.

## Installation

The installation script (`install-memory-system.sh`) automatically installs this agent to `~/.claude/agents/memory-only.md`.

## How It Works

When a skill like `memory-store` runs, it uses:
```
Task tool with subagent_type: "memory-only"
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

All memories use this metadata format (V7 design):
```json
{
  "title": "Plain text title",
  "preview": "2-3 sentence summary",
  "content": "[Full formatted markdown document]"
}
```

The `content` field contains the complete formatted markdown including tags, memory type, and role information embedded within the text (not as separate metadata fields).

## Verification

After installation, verify the agent is available:
```bash
ls ~/.claude/agents/memory-only.md
```

## Troubleshooting

**"memory-only not found"**
- Run installation script: `./install-memory-system.sh`
- Or manually copy: `cp subagents/memory-only/memory-only.md ~/.claude/agents/`

**"Cannot access file tools"**
- This is expected and by design
- Agent should only use MCP memory tools

## Related Files

- **Skills**: `~/.claude/skills/memory-{store,recall}/`
- **MCP Server**: Configured in `~/.claude/mcp.json` (or similar)
- **Hooks**: `~/.claude/hooks/memory_*.py` (automation)
