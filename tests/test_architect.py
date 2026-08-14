from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.schemas.viral_template import ViralTemplate


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """Fixture for FastAPI TestClient."""
    with TestClient(app) as c:
        yield c


def test_architect_alignment_success(client: TestClient) -> None:
    """Test the /api/v1/architect endpoint with mocked Gemini/VertexAI response and mocked MCP fetch."""
    with patch("backend.agents.architect.genai.Client") as mock_client_factory:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = (
            '{"adapted_beat_sheet": {'
            '"title": "Adapted Formula", '
            '"total_duration": 60, '
            '"pacing_score": 8.5, '
            '"beats": [], '
            '"viral_summary": "Good engagement", '
            '"hook_analysis": "Reworked opening mirrors the reference cold open.", '
            '"pacing_curve": ["fast", "climax"], '
            '"key_events": [{"timestamp": "0:02", "event_description": "New hook"}]'
            '}, '
            '"structural_alignment_notes": ["Preserved the fast cold open"], '
            '"creative_deviations": ["Swapped the climax setting per creative brief"]}'
        )
        mock_client.aio.models.generate_content = AsyncMock(return_value=mock_response)
        mock_client_factory.return_value = mock_client

        canned_templates = [
            ViralTemplate(pattern_id="p1", pattern_type="hook", description="Cold open hook", source_ref="video-123")
        ]

        with patch("backend.agents.architect.fetch_viral_templates", new=AsyncMock(return_value=canned_templates)):
            response = client.post(
                "/api/v1/architect",
                json={
                    "beat_sheet": {
                        "title": "Formula Breakdown",
                        "total_duration": 60,
                        "pacing_score": 8.8,
                        "beats": [],
                        "viral_summary": "High retention pacing structure.",
                        "hook_analysis": "The video starts with a high-energy transition.",
                        "pacing_curve": ["fast", "slow build", "climax"],
                        "key_events": [{"timestamp": "0:01", "event_description": "Initial transition hook"}],
                    },
                    "creative_brief": "Adapt this for a cooking channel with a twist ending.",
                },
            )

            assert response.status_code == 200
            data = response.json()
            assert data["adapted_beat_sheet"]["hook_analysis"] == "Reworked opening mirrors the reference cold open."
            assert data["structural_alignment_notes"] == ["Preserved the fast cold open"]
            assert data["creative_deviations"] == ["Swapped the climax setting per creative brief"]

            mock_client_factory.assert_called_once()
