"""Shared pytest fixtures/helpers for exercising the real FastAPI app with mocked Gemini calls."""

import socket
import threading
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import requests
import uvicorn
from streamlit.testing.v1 import AppTest
from streamlit.testing.v1.element_tree import Button

from backend.main import app


def click_button(at: AppTest, label: str) -> Button:
    """Find a button by its label (partial match) in an AppTest session (raises if not found)."""
    for b in at.button:
        if label.lower() in b.label.lower():
            return b
    raise AssertionError(f"Button with text containing {label!r} not found. Available buttons: {[b.label for b in at.button]}")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.fixture
def live_backend_url() -> Generator[str, None, None]:
    """Run the real FastAPI app on a background thread for genuine HTTP integration tests."""
    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    base_url = f"http://127.0.0.1:{port}"
    for _ in range(50):
        try:
            requests.get(f"{base_url}/health", timeout=0.5)
            break
        except requests.RequestException:
            time.sleep(0.1)
    else:
        raise RuntimeError("Live backend did not become ready in time")

    yield base_url

    server.should_exit = True
    thread.join(timeout=5.0)


@contextmanager
def mocked_gemini_pipeline(beat_sheet_json: str, blueprint_json: str, assets_json: str) -> Generator[None]:
    """Patch Gemini + MCP calls so the real agent pipeline returns canned JSON per stage.

    Dispatches on distinctive substrings in each agent's prompt (see deconstructor.py/
    architect.py/director.py) since all three agents share the same mocked model instance.
    """
    mock_client = MagicMock()

    async def _fake_generate_content(*, model: str, contents: str, config: Any = None) -> MagicMock:
        response = MagicMock()
        if "Reference Beat Sheet" in contents:
            response.text = blueprint_json
        elif "Blueprint:" in contents:
            response.text = assets_json
        else:
            response.text = beat_sheet_json
        return response

    mock_client.aio.models.generate_content = AsyncMock(side_effect=_fake_generate_content)

    with (
        patch("backend.agents.deconstructor.genai.Client", return_value=mock_client),
        patch("backend.agents.architect.genai.Client", return_value=mock_client),
        patch("backend.agents.director.genai.Client", return_value=mock_client),
        patch("backend.agents.architect.fetch_viral_templates", new=AsyncMock(return_value=[])),
    ):
        yield
