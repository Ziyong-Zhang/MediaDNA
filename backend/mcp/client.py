"""In-process wrapper letting backend/agent code fetch MCP tool results directly.

Agents call this plain async function rather than spawning an MCP client/subprocess,
keeping MCP transport details out of agent logic while still routing all ClickHouse
access through the F03 MCP tool definition.
"""

from backend.mcp.server import get_viral_templates
from backend.schemas.viral_template import ViralTemplate


async def fetch_viral_templates(pattern_type: str | None = None, limit: int = 20) -> list[ViralTemplate]:
    """Fetch viral templates via the `get_viral_templates` MCP tool, in-process.

    Args:
        pattern_type: Optional category filter (e.g. 'hook', 'pacing', 'twist').
        limit: Maximum number of rows to return.
    """
    return await get_viral_templates(pattern_type=pattern_type, limit=limit)
