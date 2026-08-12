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


def test_deconstruct_media_success(client: TestClient) -> None:
    """Test the /api/v1/deconstruct endpoint with mocked Gemini/VertexAI response."""
    # Mock Vertex AI Initialization
    with patch("google.cloud.aiplatform.init") as mock_init:
        # Mock GenerativeModel and GenerationConfig
        mock_model_instance = MagicMock()
        mock_response = MagicMock()
        mock_response.text = (
            '{"hook_analysis": "The video starts with a high-energy transition.", '
            '"pacing_curve": ["fast", "slow build", "climax"], '
            '"key_events": [{"timestamp": "0:01", "event_description": "Initial transition hook"}, '
            '{"timestamp": "0:15", "event_description": "Body discussion"}]}'
        )
        mock_model_instance.generate_content.return_value = mock_response

        with patch("vertexai.generative_models.GenerativeModel", return_value=mock_model_instance), \
             patch("vertexai.generative_models.GenerationConfig"):

            response = client.post(
                "/api/v1/deconstruct",
                json={"content": "Welcome to my video! Here we go. Now we discuss the core concepts. Thanks for watching."}
            )

            assert response.status_code == 200
            data = response.json()
            assert data["hook_analysis"] == "The video starts with a high-energy transition."
            assert data["pacing_curve"] == ["fast", "slow build", "climax"]
            assert len(data["key_events"]) == 2
            assert data["key_events"][0]["timestamp"] == "0:01"
            assert data["key_events"][0]["event_description"] == "Initial transition hook"
            
            mock_init.assert_called_once()
