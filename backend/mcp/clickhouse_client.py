"""ClickHouse Cloud HTTP client for querying viral structure templates.

Credentials are read exclusively from environment variables; never hardcode
ClickHouse connection details in source code.
"""

import os
from typing import Any

import httpx

from backend.schemas.viral_template import ViralTemplate

_REQUIRED_ENV_VARS = ("CLICKHOUSE_HOST", "CLICKHOUSE_PORT", "CLICKHOUSE_USER", "CLICKHOUSE_PASSWORD")


class ClickHouseConfigError(RuntimeError):
    """Raised when required ClickHouse connection environment variables are missing."""


def _get_connection_settings() -> dict[str, str]:
    missing = [name for name in _REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise ClickHouseConfigError(f"Missing required ClickHouse environment variable(s): {', '.join(missing)}")
    return {name: os.environ[name] for name in _REQUIRED_ENV_VARS}


async def query_viral_templates(pattern_type: str | None = None, limit: int = 20) -> list[ViralTemplate]:
    """Query the `viral_templates` table in ClickHouse Cloud over its HTTP interface.

    Args:
        pattern_type: Optional category filter (e.g. 'hook', 'pacing', 'twist').
        limit: Maximum number of rows to return.

    Returns:
        A list of parsed `ViralTemplate` rows.
    """
    settings = _get_connection_settings()
    secure = os.getenv("CLICKHOUSE_SECURE", "True").lower() != "false"
    scheme = "https" if secure else "http"
    url = f"{scheme}://{settings['CLICKHOUSE_HOST']}:{settings['CLICKHOUSE_PORT']}/"

    query_params: dict[str, Any] = {"limit_value": limit}
    where_clause = ""
    if pattern_type is not None:
        where_clause = "WHERE pattern_type = {pattern_type_value:String}"
        query_params["pattern_type_value"] = pattern_type

    query = (
        "SELECT pattern_id, pattern_type, description, source_ref "
        f"FROM viral_templates {where_clause} "
        "LIMIT {limit_value:UInt32} FORMAT JSON"
    )

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            url,
            params={"query": query, **query_params},
            auth=(settings["CLICKHOUSE_USER"], settings["CLICKHOUSE_PASSWORD"]),
        )
        response.raise_for_status()
        payload = response.json()

    return [ViralTemplate.model_validate(row) for row in payload.get("data", [])]
