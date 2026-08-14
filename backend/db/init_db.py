"""Script to initialize the ClickHouse database schema for MediaDNA.

Creates the `viral_templates` table if it does not already exist.
"""

import asyncio
import os
from pathlib import Path

import httpx

_REQUIRED_ENV_VARS = ("CLICKHOUSE_HOST", "CLICKHOUSE_PORT", "CLICKHOUSE_USER", "CLICKHOUSE_PASSWORD")


def load_env() -> None:
    """Load environment variables from the root .env file if present."""
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.exists():
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split("=", 1)
                if len(parts) == 2:
                    key, val = parts[0].strip(), parts[1].strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    os.environ.setdefault(key, val)


class ClickHouseConfigError(RuntimeError):
    """Raised when ClickHouse configuration is missing or invalid."""


def _get_connection_settings() -> dict[str, str]:
    missing = [name for name in _REQUIRED_ENV_VARS if not os.getenv(name)]
    if missing:
        raise ClickHouseConfigError(f"Missing required ClickHouse environment variable(s): {', '.join(missing)}")
    return {name: os.environ[name] for name in _REQUIRED_ENV_VARS}


async def init_db() -> None:
    """Create necessary tables in ClickHouse Cloud."""
    load_env()
    settings = _get_connection_settings()
    secure = os.getenv("CLICKHOUSE_SECURE", "True").lower() != "false"
    scheme = "https" if secure else "http"
    url = f"{scheme}://{settings['CLICKHOUSE_HOST']}:{settings['CLICKHOUSE_PORT']}/"

    query = """
    CREATE TABLE IF NOT EXISTS viral_templates (
        pattern_id String,
        pattern_type String,
        description String,
        source_ref String
    ) ENGINE = MergeTree()
    ORDER BY pattern_id;
    """

    print(f"Connecting to ClickHouse at {scheme}://{settings['CLICKHOUSE_HOST']}...")
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            url,
            params={"query": query},
            auth=(settings["CLICKHOUSE_USER"], settings["CLICKHOUSE_PASSWORD"]),
        )
        if response.status_code != 200:
            print(f"Failed to initialize database: {response.status_code}")
            print(response.text)
            response.raise_for_status()
        else:
            print("Successfully initialized 'viral_templates' table.")


if __name__ == "__main__":
    asyncio.run(init_db())
