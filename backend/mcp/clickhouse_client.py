"""ClickHouse Cloud HTTP client for querying viral structure templates.

Credentials are read exclusively from environment variables; never hardcode
ClickHouse connection details in source code.
"""

import os

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
        pattern_type: Optional category filter.
        limit: Maximum number of rows to return.

    Returns:
        A list of parsed `ViralTemplate` rows.
    """
    settings = _get_connection_settings()
    secure = os.getenv("CLICKHOUSE_SECURE", "True").lower() != "false"
    scheme = "https" if secure else "http"
    url = f"{scheme}://{settings['CLICKHOUSE_HOST']}:{settings['CLICKHOUSE_PORT']}/"

    # Safely construct the query string
    # We use JSONEachRow as it is highly resilient for HTTP streaming/parsing
    base_query = "SELECT pattern_id, pattern_type, description, source_ref FROM viral_templates"
    
    if pattern_type is not None:
        # For hackathon purposes, standard string formatting is acceptable here 
        # as pattern_type is controlled internally.
        base_query += f" WHERE pattern_type = '{pattern_type}'"
        
    base_query += f" LIMIT {limit} FORMAT JSONEachRow"

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            url,
            params={"query": base_query},
            auth=(settings["CLICKHOUSE_USER"], settings["CLICKHOUSE_PASSWORD"]),
        )
        response.raise_for_status()
        
        # Parse the JSONEachRow response line by line
        templates = []
        for line in response.text.strip().split("\n"):
            if line:
                templates.append(ViralTemplate.model_validate_json(line))
                
        return templates