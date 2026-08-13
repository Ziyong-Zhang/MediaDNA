import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.mcp.clickhouse_client import ClickHouseConfigError, query_viral_templates
from backend.mcp.client import fetch_viral_templates
from backend.mcp.server import server
from backend.schemas.viral_template import ViralTemplate

_ENV_VARS = {
    "CLICKHOUSE_HOST": "test.clickhouse.cloud",
    "CLICKHOUSE_PORT": "8443",
    "CLICKHOUSE_USER": "default",
    "CLICKHOUSE_PASSWORD": "secret",
}

_CANNED_ROWS = {
    "data": [
        {
            "pattern_id": "p1",
            "pattern_type": "hook",
            "description": "Cold open with a question",
            "source_ref": "video-123",
        }
    ]
}


def test_server_initializes() -> None:
    """MCP server registers the get_viral_templates tool without making any network calls."""
    tools = asyncio.run(server.list_tools())
    assert "get_viral_templates" in [tool.name for tool in tools]


def test_get_viral_templates_missing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """A clear config error is raised (not a crash) when ClickHouse credentials are unset."""
    for var in ("CLICKHOUSE_HOST", "CLICKHOUSE_PORT", "CLICKHOUSE_USER", "CLICKHOUSE_PASSWORD"):
        monkeypatch.delenv(var, raising=False)

    with pytest.raises(ClickHouseConfigError):
        asyncio.run(query_viral_templates())


def test_get_viral_templates_mocked_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """The ClickHouse HTTP client parses JSON rows into ViralTemplate objects."""
    for key, value in _ENV_VARS.items():
        monkeypatch.setenv(key, value)

    mock_response = MagicMock()
    mock_response.json.return_value = _CANNED_ROWS
    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response
    mock_client.__aenter__.return_value = mock_client

    with patch("backend.mcp.clickhouse_client.httpx.AsyncClient", return_value=mock_client):
        templates = asyncio.run(query_viral_templates(pattern_type="hook", limit=5))

    assert templates == [
        ViralTemplate(
            pattern_id="p1",
            pattern_type="hook",
            description="Cold open with a question",
            source_ref="video-123",
        )
    ]
    mock_client.post.assert_awaited_once()


def test_agent_can_fetch_templates_mocked() -> None:
    """Agent code can fetch templates in-process without touching MCP transport/ClickHouse HTTP details."""
    canned = [ViralTemplate(pattern_id="p1", pattern_type="hook", description="d", source_ref="s")]

    with patch("backend.mcp.server.query_viral_templates", new=AsyncMock(return_value=canned)):
        result = asyncio.run(fetch_viral_templates(pattern_type="hook"))

    assert result == canned
