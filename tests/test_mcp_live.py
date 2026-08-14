"""Live integration tests for the ClickHouse MCP client.

These tests run against a real ClickHouse Cloud instance. They are skipped by default
unless the `CLICKHOUSE_LIVE_TEST` environment variable is set to "true".
"""

import os

import pytest

from backend.db.init_db import load_env
from backend.mcp.client import fetch_viral_templates
from backend.schemas.viral_template import ViralTemplate

# Load the environment from .env file for local development testing
load_env()

# Skip all tests in this module unless CLICKHOUSE_LIVE_TEST is set to "true"
pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        os.getenv("CLICKHOUSE_LIVE_TEST") != "true",
        reason="Skipping live database tests. Set CLICKHOUSE_LIVE_TEST=true to run.",
    ),
]


@pytest.mark.asyncio
async def test_fetch_viral_templates_live() -> None:
    """Actually queries the real ClickHouse Cloud instance via the MCP client wrapper."""
    # Ensure standard ClickHouse credentials are loaded
    assert os.getenv("CLICKHOUSE_HOST") is not None, "CLICKHOUSE_HOST environment variable is missing"

    # Fetch templates via the in-process MCP client wrapper
    templates = await fetch_viral_templates(limit=5)

    # Check that we got a list back (could be empty if not seeded yet, or populated)
    assert isinstance(templates, list)
    for template in templates:
        assert isinstance(template, ViralTemplate)
        assert template.pattern_id is not None
        assert template.pattern_type is not None
