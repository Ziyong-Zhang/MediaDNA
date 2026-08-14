from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Fixture for FastAPI TestClient."""
    with TestClient(app) as c:
        yield c


def test_deconstruct_media_success(client: TestClient) -> None:
    """Test the /api/v1/deconstruct endpoint with mocked Gemini/VertexAI response."""
    # Mock Vertex AI Initialization
    with patch("backend.agents.deconstructor.genai.Client") as mock_client_factory:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = (
            '{"title": "Formula Breakdown", '
            '"total_duration": 60, '
            '"pacing_score": 8.8, '
            '"beats": [{"timestamp_sec": 0, "hook_type": "Visual Cliffhanger", "visual_cue": "Rapid zoom on character", '
            '"audio_cue": "Riser into silence", "emotion_shift": "Anticipation", "retention_driver": "Open Loop"}], '
            '"viral_summary": "High retention pacing structure.", '
            '"hook_analysis": "The video starts with a high-energy transition.", '
            '"pacing_curve": ["fast", "slow build", "climax"], '
            '"key_events": [{"timestamp": "0:01", "event_description": "Initial transition hook"}]}'
        )
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_client_factory.return_value = mock_client

        response = client.post(
            "/api/v1/deconstruct",
            json={
                "reference_url": "https://example.com/sample.mp4",
                "transcript": "Today we are analyzing the viral formula.",
            },
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


def test_deconstruct_empty_payload_fails(client: TestClient) -> None:
    """Test that deconstruct fails with empty payload (validation error)."""
    response = client.post(
        "/api/v1/deconstruct",
        json={}
    )
    assert response.status_code == 422  # Pydantic validation error


def test_deconstruct_with_transcript_only(client: TestClient) -> None:
    """Test deconstruct with transcript only (no reference_url)."""
    with patch("backend.agents.deconstructor.genai.Client") as mock_client_factory:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = (
            '{"title": "Transcript Analysis", "total_duration": 45, "pacing_score": 7.5, '
            '"beats": [], "viral_summary": "Moderate engagement", '
            '"hook_analysis": "Strong hook", "pacing_curve": ["fast"], "key_events": []}'
        )
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_client_factory.return_value = mock_client

        response = client.post(
            "/api/v1/deconstruct",
            json={"transcript": "Just a test transcript"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Transcript Analysis"
