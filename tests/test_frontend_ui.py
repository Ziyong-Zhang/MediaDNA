from pathlib import Path
from unittest.mock import patch

import pytest
from streamlit.testing.v1 import AppTest

from frontend import api_client
from tests.conftest import click_button, mocked_gemini_pipeline

_APP_PATH = str(Path(__file__).resolve().parent.parent / "frontend" / "app.py")

_CANNED_BEAT_SHEET = {
    "hook_analysis": "The video starts with a high-energy transition.",
    "pacing_curve": ["fast", "slow build", "climax"],
    "key_events": [{"timestamp": "0:01", "event_description": "Initial transition hook"}],
}
_CANNED_BLUEPRINT = {
    "adapted_beat_sheet": _CANNED_BEAT_SHEET,
    "structural_alignment_notes": ["Preserved the fast cold open"],
    "creative_deviations": ["Swapped the climax setting per creative brief"],
}
_CANNED_ASSETS = {
    "tts_script": [{"speaker": "Narrator", "text": "Welcome back.", "timestamp": "0:02"}],
    "visual_prompts": [{"scene_id": "scene-1", "prompt_text": "A neon-lit kitchen", "style_tags": ["cinematic"]}],
    "metadata": {"estimated_duration": "60s"},
}


def _run_deconstructor_stage(at: AppTest, transcript: str = "Welcome to my video!") -> None:
    at.radio[0].set_value("Text Transcript/Script")
    at.run()
    at.text_area[0].set_value(transcript)
    at.run()
    click_button(at, "Run Deconstructor").click().run()


def _run_architect_stage(at: AppTest, creative_brief: str = "Adapt this for a cooking channel") -> None:
    at.text_area[1].set_value(creative_brief)
    at.run()
    click_button(at, "Run Architect").click().run()


def test_deconstructor_workflow_mocked() -> None:
    """Tier 2: entering a transcript and clicking Run Deconstructor renders the mocked BeatSheet."""
    at = AppTest.from_file(_APP_PATH)
    at.run()

    with patch("frontend.api_client.deconstruct", return_value=_CANNED_BEAT_SHEET) as mock_deconstruct:
        _run_deconstructor_stage(at)

    assert not at.exception
    assert at.session_state["beat_sheet"] == _CANNED_BEAT_SHEET
    mock_deconstruct.assert_called_once_with("Welcome to my video!")


def test_architect_workflow_mocked() -> None:
    """Tier 2: after a BeatSheet exists, submitting a creative brief renders the mocked Blueprint."""
    at = AppTest.from_file(_APP_PATH)
    at.run()

    with patch("frontend.api_client.deconstruct", return_value=_CANNED_BEAT_SHEET):
        _run_deconstructor_stage(at)

    with patch("frontend.api_client.architect", return_value=_CANNED_BLUEPRINT) as mock_architect:
        _run_architect_stage(at)

    assert not at.exception
    assert at.session_state["blueprint"] == _CANNED_BLUEPRINT
    mock_architect.assert_called_once_with(_CANNED_BEAT_SHEET, "Adapt this for a cooking channel")


def test_director_workflow_mocked() -> None:
    """Tier 2: after a Blueprint exists, clicking Run Director renders the mocked ProductionAssets."""
    at = AppTest.from_file(_APP_PATH)
    at.run()

    with patch("frontend.api_client.deconstruct", return_value=_CANNED_BEAT_SHEET):
        _run_deconstructor_stage(at)
    with patch("frontend.api_client.architect", return_value=_CANNED_BLUEPRINT):
        _run_architect_stage(at)

    with patch("frontend.api_client.produce", return_value=_CANNED_ASSETS) as mock_produce:
        click_button(at, "Run Director").click().run()

    assert not at.exception
    assert at.session_state["production_assets"] == _CANNED_ASSETS
    mock_produce.assert_called_once_with(_CANNED_BLUEPRINT)


def test_deconstructor_workflow_live_backend(monkeypatch: pytest.MonkeyPatch, live_backend_url: str) -> None:
    """Tier 3: the Deconstructor click-path round-trips through the real FastAPI app (mocked Gemini only)."""
    monkeypatch.setattr(api_client, "BACKEND_URL", live_backend_url)

    beat_sheet_json = (
        '{"hook_analysis": "Cold open with a question.", '
        '"pacing_curve": ["fast", "climax"], '
        '"key_events": [{"timestamp": "0:01", "event_description": "Hook"}]}'
    )

    at = AppTest.from_file(_APP_PATH)
    at.run()

    with mocked_gemini_pipeline(beat_sheet_json, "{}", "{}"):
        _run_deconstructor_stage(at)

    assert not at.exception
    assert at.session_state["beat_sheet"]["hook_analysis"] == "Cold open with a question."
