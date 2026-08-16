import asyncio
import json
from collections.abc import Generator
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.schemas.beat_sheet import BeatSheet

_BEAT_SHEET_JSON = json.dumps(
    {
        "title": "Formula Breakdown",
        "total_duration": 60,
        "pacing_score": 8.8,
        "beats": [
            {
                "timestamp_sec": 0,
                "hook_type": "Visual Cliffhanger",
                "visual_cue": "Rapid zoom on character",
                "audio_cue": "Riser into silence",
                "emotion_shift": "Anticipation",
                "retention_driver": "Open Loop",
            }
        ],
        "viral_summary": "High retention pacing structure.",
        "hook_analysis": "The video starts with a high-energy transition.",
        "pacing_curve": ["fast", "slow build", "climax"],
        "key_events": [{"timestamp": "0:01", "event_description": "Initial transition hook"}],
    }
)


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Fixture for FastAPI TestClient."""
    with TestClient(app) as c:
        yield c


def _mock_gemini_response() -> MagicMock:
    """Return a MagicMock client whose async generate_content returns a canned BeatSheet JSON."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = _BEAT_SHEET_JSON
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
    return mock_client


def test_deconstruct_media_success(client: TestClient) -> None:
    """Test the /api/v1/deconstruct endpoint with a transcript via multipart form data."""
    with patch("backend.agents.deconstructor.genai.Client") as mock_client_factory:
        mock_client_factory.return_value = _mock_gemini_response()

        response = client.post(
            "/api/v1/deconstruct",
            data={"transcript": "Today we are analyzing the viral formula."},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Formula Breakdown"
        assert data["total_duration"] == 60
        assert data["pacing_score"] == 8.8
        assert len(data["beats"]) == 1
        assert data["beats"][0]["hook_type"] == "Visual Cliffhanger"
        assert data["viral_summary"] == "High retention pacing structure."
        assert data["hook_analysis"] == "The video starts with a high-energy transition."
        assert len(data["key_events"]) == 1

        mock_client_factory.assert_called_once()


def test_deconstruct_file_upload(client: TestClient) -> None:
    """Test /api/v1/deconstruct with a multipart file upload, asserting cleanup is called."""
    with (
        patch("backend.agents.deconstructor.genai.Client") as mock_client_factory,
        patch("backend.main.cleanup_file") as mock_cleanup,
    ):
        mock_client_factory.return_value = _mock_gemini_response()

        response = client.post(
            "/api/v1/deconstruct",
            data={"transcript": "Analyze this media."},
            files={"file": ("sample.m4a", b"fake-audio", "audio/mp4")},
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Formula Breakdown"

        # The temporarily saved upload must be cleaned up in a finally block
        mock_cleanup.assert_called_once()


def test_deconstruct_reference_url(client: TestClient, tmp_path: Path) -> None:
    """Test /api/v1/deconstruct with a reference URL, asserting download + cleanup happen."""
    media_path = tmp_path / "sample.m4a"
    media_path.write_bytes(b"fake-audio")

    with (
        patch("backend.agents.deconstructor.genai.Client") as mock_client_factory,
        patch("backend.main.download_youtube_audio", return_value=media_path) as mock_download,
        patch("backend.main.cleanup_file") as mock_cleanup,
    ):
        mock_client_factory.return_value = _mock_gemini_response()

        response = client.post(
            "/api/v1/deconstruct",
            data={
                "transcript": "Analyze this media.",
                "reference_url": "https://www.youtube.com/watch?v=abc123",
            },
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Formula Breakdown"

        mock_download.assert_called_once_with("https://www.youtube.com/watch?v=abc123")
        mock_cleanup.assert_called_once_with(media_path)


def test_deconstruct_optional_transcript_uses_fallback(client: TestClient) -> None:
    """Test that omitting the transcript still succeeds using the default analysis prompt."""
    with patch("backend.agents.deconstructor.genai.Client") as mock_client_factory:
        mock_client = _mock_gemini_response()
        mock_client_factory.return_value = mock_client

        response = client.post(
            "/api/v1/deconstruct",
            data={},
        )

        assert response.status_code == 200
        assert response.json()["title"] == "Formula Breakdown"

        generate_kwargs = mock_client.aio.models.generate_content.call_args.kwargs
        contents = generate_kwargs["contents"]
        assert any(
            isinstance(part, str) and "Analyze this reference media" in part
            for part in contents
        )


def test_deconstruct_with_transcript_only(client: TestClient) -> None:
    """Test deconstruct with transcript only (no reference_url or file)."""
    with patch("backend.agents.deconstructor.genai.Client") as mock_client_factory:
        mock_client_factory.return_value = _mock_gemini_response()

        response = client.post(
            "/api/v1/deconstruct",
            data={"transcript": "Just a test transcript"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Formula Breakdown"


def test_extract_beat_sheet_multimodal(tmp_path: Path) -> None:
    """Test that multimodal uploads are processed using inline bytes."""
    media_path = tmp_path / "sample.m4a"
    fake_audio_bytes = b"fake-audio"
    media_path.write_bytes(fake_audio_bytes)

    with patch("backend.agents.deconstructor.genai.Client") as mock_client_factory:
        mocked_client = MagicMock()

        response_json = {
            "title": "Multimodal Breakdown",
            "total_duration": 45,
            "pacing_score": 8.2,
            "beats": [],
            "viral_summary": "High retention pacing structure.",
            "hook_analysis": "The video opens with a clear high-energy moment.",
            "pacing_curve": ["fast", "slow build", "climax"],
            "key_events": [],
        }
        mock_response = MagicMock()
        mock_response.text = json.dumps(response_json)
        mocked_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_client_factory.return_value = mocked_client

        agent = __import__("backend.agents.deconstructor", fromlist=["DeconstructorAgent"]).DeconstructorAgent()
        beat_sheet = asyncio.run(agent.extract_beat_sheet(text_content="Analyze this media.", media_path=media_path))

        assert isinstance(beat_sheet, BeatSheet)

        # Verify the contents payload contains the inline bytes and the prompt
        generate_kwargs = mocked_client.aio.models.generate_content.call_args.kwargs
        contents = generate_kwargs["contents"]

        assert isinstance(contents, list)
        assert len(contents) == 2

        # Check the Inline Data Part
        audio_part = contents[0]
        # In the Google GenAI SDK, types.Part.from_bytes sets the inline_data attribute
        assert audio_part.inline_data.data == fake_audio_bytes
        assert audio_part.inline_data.mime_type == "audio/mp4"

        # Check the Text Prompt
        assert "Analyze this media." in contents[1]