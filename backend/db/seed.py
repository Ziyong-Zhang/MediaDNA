"""Script to seed high-quality reference records into ClickHouse Cloud.

This populates the `viral_templates` table with three YouTube-style themes
to showcase diverse pacing structures.
"""

import asyncio
import json
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


async def seed_db() -> None:
    """Seed the `viral_templates` table with diverse pacing structure templates."""
    load_env()
    settings = _get_connection_settings()
    secure = os.getenv("CLICKHOUSE_SECURE", "True").lower() != "false"
    scheme = "https" if secure else "http"
    url = f"{scheme}://{settings['CLICKHOUSE_HOST']}:{settings['CLICKHOUSE_PORT']}/"

    # Define the 3 high-quality YouTube-style reference records matching ViralTemplate schema
    seed_records = [
        {
            "pattern_id": "high_energy_bouldering_vlog",
            "pattern_type": "pacing",
            "description": "High-Energy Bouldering Vlog: Features a fast hook, dynamic problem-solving pacing, and rapid cuts to sustain high viewer attention.",
            "source_ref": "YouTube / Creator Economy (Outdoor Sports Vlog)",
        },
        {
            "pattern_id": "immersive_alpine_citywalk",
            "pattern_type": "pacing",
            "description": "Immersive Alpine Citywalk: Features an atmospheric slow build, deep environmental storytelling, and steady, unhurried pacing.",
            "source_ref": "Streaming Media / Travel / ASMR (Cinematic Street Walk)",
        },
        {
            "pattern_id": "viral_tech_podcast",
            "pattern_type": "pacing",
            "description": "Viral Tech Podcast: Optimized for multi-speaker debates, clear chapter markers, and a strong, high-conversion Call to Action (CTA).",
            "source_ref": "Tech Media / Video Podcast (Dynamic Interview)",
        },
    ]

    print(f"Connecting to ClickHouse at {scheme}://{settings['CLICKHOUSE_HOST']} to seed data...")

    # Format the data as JSONEachRow
    data = "\n".join(json.dumps(record) for record in seed_records)
    query = "INSERT INTO viral_templates FORMAT JSONEachRow"

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            url,
            params={"query": query},
            content=data,
            auth=(settings["CLICKHOUSE_USER"], settings["CLICKHOUSE_PASSWORD"]),
        )
        if response.status_code != 200:
            print(f"Failed to seed database: {response.status_code}")
            print(response.text)
            response.raise_for_status()
        else:
            print(f"Successfully seeded {len(seed_records)} templates into 'viral_templates'.")


if __name__ == "__main__":
    asyncio.run(seed_db())
