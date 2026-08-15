"""HTTP client isolating all backend calls from the Streamlit UI.

This is the only module under `frontend/` permitted to talk to the backend;
UI code must call these functions instead of using `requests` directly,
preserving the project's strict UI/backend decoupling constraint.
"""

import os
from typing import Any

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class BackendError(RuntimeError):
    """Raised when a backend call fails (non-200 response or network error)."""


def _post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{BACKEND_URL}{path}"
    try:
        response = requests.post(url, json=payload, timeout=60.0)
    except requests.RequestException as e:
        raise BackendError(f"Request to {url} failed: {e}") from e

    if response.status_code != 200:
        raise BackendError(f"Request to {url} returned HTTP {response.status_code}: {response.text}")

    result: dict[str, Any] = response.json()
    return result


def deconstruct(content: str) -> dict[str, Any]:
    """Call POST /api/v1/deconstruct with transcript and return the resulting BeatSheet as a dict."""
    return _post("/api/v1/deconstruct", {"transcript": content})


def architect(beat_sheet: dict[str, Any], creative_brief: str) -> dict[str, Any]:
    """Call POST /api/v1/architect and return the resulting Blueprint as a dict."""
    return _post("/api/v1/architect", {"beat_sheet": beat_sheet, "creative_brief": creative_brief})


def produce(blueprint: dict[str, Any]) -> dict[str, Any]:
    """Call POST /api/v1/produce and return the resulting ProductionAssets as a dict."""
    return _post("/api/v1/produce", blueprint)


def health() -> dict[str, Any]:
    """Call GET /health and return the response as a dict."""
    url = f"{BACKEND_URL}/health"
    try:
        response = requests.get(url, timeout=5.0)
    except requests.RequestException as e:
        raise BackendError(f"Request to {url} failed: {e}") from e

    if response.status_code != 200:
        raise BackendError(f"Request to {url} returned HTTP {response.status_code}: {response.text}")

    result: dict[str, Any] = response.json()
    return result

