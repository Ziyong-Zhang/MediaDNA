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


def test_produce_assets_success(client: TestClient) -> None:
    """Test the /api/v1/produce endpoint with mocked Gemini/VertexAI response."""
    with patch("backend.agents.director.genai.Client") as mock_client_factory:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = (
            '{"metadata": {"title": "Test Campaign", "target_platform": "tiktok", "estimated_duration": "60s"}, '
            '"pacing_curve": ["Hook", "Build"], '
            '"tts_script": [{"speaker": "Narrator", "text": "Welcome back.", "timestamp": "0:02", "emotion_tag": "energetic"}], '
            '"storyboard_panels": [{"scene_id": "scene-1", "imagen_prompt": "A neon-lit kitchen at night, cinematic", '
            '"camera_angle": "Wide shot"}]}'
        )
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_client_factory.return_value = mock_client

        response = client.post(
            "/api/v1/produce",
            json={
                "adapted_beat_sheet": {
                    "title": "Adapted Formula",
                    "total_duration": 60,
                    "pacing_score": 8.5,
                    "beats": [],
                    "viral_summary": "Good engagement",
                    "hook_analysis": "Reworked opening mirrors the reference cold open.",
                    "pacing_curve": ["fast", "climax"],
                    "key_events": [{"timestamp": "0:02", "event_description": "New hook"}],
                },
                "structural_alignment_notes": ["Preserved the fast cold open"],
                "creative_deviations": ["Swapped the climax setting per creative brief"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["tts_script"] == [
            {"speaker": "Narrator", "text": "Welcome back.", "timestamp": "0:02", "emotion_tag": "energetic"}
        ]
        assert data["storyboard_panels"][0]["scene_id"] == "scene-1"
        assert data["metadata"]["target_platform"] == "tiktok"

        mock_client_factory.assert_called_once()
