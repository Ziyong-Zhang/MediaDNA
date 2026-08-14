from collections.abc import Generator
from unittest.mock import MagicMock, patch

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
    with patch("google.cloud.aiplatform.init") as mock_init:
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = (
            '{"metadata": {"title": "Test Campaign", "target_platform": "tiktok", "estimated_duration": "60s"}, '
            '"pacing_curve": ["Hook", "Build"], '
            '"tts_script": [{"speaker": "Narrator", "text": "Welcome back.", "timestamp": "0:02", "emotion_tag": "energetic"}], '
            '"storyboard_panels": [{"scene_id": "scene-1", "imagen_prompt": "A neon-lit kitchen at night, cinematic", '
            '"camera_angle": "Wide shot"}]}'
        )
        mock_model_instance.generate_content.return_value = mock_response

        with (
            patch("vertexai.generative_models.GenerativeModel", return_value=mock_model_instance),
            patch("vertexai.generative_models.GenerationConfig"),
        ):
            response = client.post(
                "/api/v1/produce",
                json={
                    "adapted_beat_sheet": {
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

            mock_init.assert_called_once()
