"""FastMCP server for memory system.

This module initializes the MCP server and imports all tool modules
for auto-registration via decorators.

CRITICAL: Logging must go to stderr (stdout reserved for MCP protocol).
"""

import logging
import sys

# CRITICAL: Configure logging to stderr (stdout is reserved for MCP JSON-RPC protocol)
# This prevents silent failures where server appears to start but cannot communicate
logging.basicConfig(
    level=logging.INFO,
    stream=sys.stderr,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server (following Python MCP naming convention)
mcp = FastMCP("memory_mcp")

# Import tool modules for auto-registration
# Tools register themselves via @mcp.tool decorators
from .tools import search_tools, mutation_tools, admin_tools

logger.info("Memory MCP server initialized with 8 tools")

if __name__ == "__main__":
    logger.info("Starting Memory MCP server on stdio transport")
    mcp.run()  # stdio transport
