from unittest.mock import MagicMock, patch

import pytest
import requests

from frontend import api_client
from frontend.api_client import BackendError
from tests.conftest import mocked_gemini_pipeline


def test_deconstruct_mocked_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tier 2: deconstruct() parses a mocked 200 response into a dict."""
    monkeypatch.setattr(api_client, "BACKEND_URL", "http://backend.invalid")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"hook_analysis": "x", "pacing_curve": ["fast"], "key_events": []}

    with patch("frontend.api_client.requests.post", return_value=mock_response) as mock_post:
        result = api_client.deconstruct("some transcript")

    assert result["hook_analysis"] == "x"
    mock_post.assert_called_once()


def test_deconstruct_error_on_non_200(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tier 2: deconstruct() raises BackendError on a non-200 response."""
    monkeypatch.setattr(api_client, "BACKEND_URL", "http://backend.invalid")

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "internal error"

    with patch("frontend.api_client.requests.post", return_value=mock_response), pytest.raises(BackendError):
        api_client.deconstruct("some transcript")


def test_deconstruct_error_on_request_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tier 2: deconstruct() raises BackendError when requests raises a RequestException."""
    monkeypatch.setattr(api_client, "BACKEND_URL", "http://backend.invalid")

    with (
        patch("frontend.api_client.requests.post", side_effect=requests.ConnectionError("boom")),
        pytest.raises(BackendError),
    ):
        api_client.deconstruct("some transcript")


def test_full_pipeline_against_live_backend_mocked_gemini(monkeypatch: pytest.MonkeyPatch, live_backend_url: str) -> None:
    """Tier 3: api_client functions round-trip through the real FastAPI app + agents (mocked Gemini only)."""
    monkeypatch.setattr(api_client, "BACKEND_URL", live_backend_url)

    beat_sheet_json = (
        '{"hook_analysis": "Cold open with a question.", '
        '"pacing_curve": ["fast", "climax"], '
        '"key_events": [{"timestamp": "0:01", "event_description": "Hook"}]}'
    )
    blueprint_json = (
        '{"adapted_beat_sheet": {"hook_analysis": "Adapted hook.", "pacing_curve": ["fast"], '
        '"key_events": [{"timestamp": "0:01", "event_description": "New hook"}]}, '
        '"structural_alignment_notes": ["kept the cold open"], '
        '"creative_deviations": ["changed the setting"]}'
    )
    assets_json = (
        '{"metadata": {"title": "Test", "target_platform": "YouTube", "estimated_duration": "30s"}, '
        '"pacing_curve": ["Hook", "Build"], '
        '"tts_script": [{"speaker": "Narrator", "text": "Hi.", "timestamp": "0:01", "emotion_tag": "energetic"}], '
        '"storyboard_panels": [{"scene_id": "s1", "imagen_prompt": "A kitchen", "camera_angle": "Wide"}]}'
    )

    with mocked_gemini_pipeline(beat_sheet_json, blueprint_json, assets_json):
        beat_sheet = api_client.deconstruct("Welcome to my video!")
        blueprint = api_client.architect(beat_sheet, "Make it a cooking channel twist")
        assets = api_client.produce(blueprint)

    assert beat_sheet["hook_analysis"] == "Cold open with a question."
    assert blueprint["structural_alignment_notes"] == ["kept the cold open"]
    assert assets["metadata"]["estimated_duration"] == "30s"


def test_health_mocked_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tier 2: health() parses a mocked 200 response into a dict."""
    monkeypatch.setattr(api_client, "BACKEND_URL", "http://backend.invalid")

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "ok", "service": "MediaDNA Backend", "version": "0.1.0"}

    with patch("frontend.api_client.requests.get", return_value=mock_response):
        result = api_client.health()

    assert result["status"] == "ok"

