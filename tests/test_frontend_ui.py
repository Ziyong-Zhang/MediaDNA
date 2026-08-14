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
_CANNED_PRODUCTION_ASSETS = {
    "metadata": {
        "title": "Test Campaign",
        "target_platform": "YouTube",
        "estimated_duration": "60s",
    },
    "pacing_curve": ["Hook", "Build", "Climax"],
    "tts_script": [{"speaker": "Narrator", "text": "Welcome back.", "timestamp": "0:02", "emotion_tag": "energetic"}],
    "storyboard_panels": [{"scene_id": "scene-1", "imagen_prompt": "A kitchen", "camera_angle": "Wide"}],
}


def _disable_mock_mode(at: AppTest) -> None:
    """Disable mock mode so the app enters live pipeline mode."""
    # Find and uncheck the mock mode checkbox
    for checkbox in at.checkbox:
        if "MOCK MODE" in str(checkbox.label):
            checkbox.uncheck()
            break
    at.run()


def test_mock_mode_default_loads_assets() -> None:
    """Tier 2: By default, mock mode is enabled and Production Assets are loaded without API calls."""
    at = AppTest.from_file(_APP_PATH)
    at.run()

    # Assert that mock mode checkbox exists and is checked by default
    assert any("MOCK MODE" in str(cb.label) for cb in at.checkbox), "Mock mode checkbox not found"
    
    # Assert production_assets are in session_state (mock mode auto-loads them)
    assert "production_assets" in at.session_state
    assert at.session_state["production_assets"]["metadata"]["title"] == "Conquer the Trail: Premium Hiking Boot Campaign"
    
    # Assert the UI renders the assets dashboard
    assert not at.exception


def test_deconstructor_workflow_mocked() -> None:
    """Tier 2: In live mode, entering a transcript and clicking Run Pipeline executes the full pipeline."""
    at = AppTest.from_file(_APP_PATH)
    at.run()

    # Disable mock mode to enter live pipeline mode
    _disable_mock_mode(at)

    # Enter a transcript
    transcript = "Welcome to my video!"
    at.text_area[0].set_value(transcript)
    at.run()

    # Mock the three API calls and run the pipeline
    with patch("frontend.api_client.deconstruct", return_value=_CANNED_BEAT_SHEET), \
         patch("frontend.api_client.architect", return_value=_CANNED_BLUEPRINT), \
         patch("frontend.api_client.produce", return_value=_CANNED_PRODUCTION_ASSETS):
        click_button(at, "Run Full Pipeline").click().run()

    assert not at.exception
    assert "production_assets" in at.session_state
    assert at.session_state["production_assets"]["metadata"]["title"] == "Test Campaign"


def test_live_mode_renders_production_assets() -> None:
    """Tier 2: When production_assets are in session_state, the dashboard renders correctly."""
    at = AppTest.from_file(_APP_PATH)
    at.run()

    # Disable mock mode first
    _disable_mock_mode(at)

    # Inject production assets directly into session_state
    at.session_state["production_assets"] = _CANNED_PRODUCTION_ASSETS
    at.run()

    assert not at.exception
    # Check that the dashboard is rendered with key elements
    assert len(at.columns) > 0, "Dashboard columns not rendered"
    assert len(at.subheader) > 0, "Dashboard subheaders not rendered"


def test_deconstructor_workflow_live_backend(monkeypatch: pytest.MonkeyPatch, live_backend_url: str) -> None:
    """Tier 3: the full pipeline round-trips through the real FastAPI app (mocked Gemini only)."""
    monkeypatch.setattr(api_client, "BACKEND_URL", live_backend_url)

    at = AppTest.from_file(_APP_PATH)
    at.run()

    # Disable mock mode
    _disable_mock_mode(at)

    transcript = "Welcome to my video!"
    at.text_area[0].set_value(transcript)
    at.run()

    beat_sheet_json = (
        '{"hook_analysis": "Cold open with a question.", '
        '"pacing_curve": ["fast", "climax"], '
        '"key_events": [{"timestamp": "0:01", "event_description": "Hook"}]}'
    )
    blueprint_json = '{"adapted_beat_sheet": {}, "structural_alignment_notes": [], "creative_deviations": []}'
    assets_json = (
        '{"metadata": {"title": "Test"}, "pacing_curve": ["Hook"], '
        '"tts_script": [{"speaker": "N", "text": "T", "timestamp": "0", "emotion_tag": "e"}], '
        '"storyboard_panels": [{"scene_id": "s", "imagen_prompt": "p", "camera_angle": "a"}]}'
    )

    with mocked_gemini_pipeline(beat_sheet_json, blueprint_json, assets_json):
        click_button(at, "Run Full Pipeline").click().run()

    assert not at.exception
    assert "production_assets" in at.session_state
