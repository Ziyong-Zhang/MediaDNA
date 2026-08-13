"""MCP server exposing ClickHouse Cloud viral-pattern data as agent tools.

Per the project's strict decoupling constraint, this is the only module that
agents/backend code may use to reach ClickHouse Cloud (no raw SQL/ORM elsewhere).
"""

from mcp.server.mcpserver import MCPServer

from backend.mcp.clickhouse_client import query_viral_templates
from backend.schemas.viral_template import ViralTemplate

server = MCPServer("mediadna-clickhouse")


@server.tool()
async def get_viral_templates(pattern_type: str | None = None, limit: int = 20) -> list[ViralTemplate]:
    """Fetch viral content structure templates stored in ClickHouse Cloud.

    Args:
        pattern_type: Optional category filter (e.g. 'hook', 'pacing', 'twist').
        limit: Maximum number of rows to return.
    """
    return await query_viral_templates(pattern_type=pattern_type, limit=limit)


if __name__ == "__main__":
    server.run()
