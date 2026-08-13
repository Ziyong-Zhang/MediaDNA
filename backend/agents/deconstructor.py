import json
import os
from typing import Any

from google.cloud import aiplatform

from backend.schemas.beat_sheet import BeatSheet


class DeconstructorAgent:
    """Deconstructor agent for extracting structured Beat Sheets from unstructured reference media."""

    def __init__(self) -> None:
        """Initialize the Deconstructor agent.
        
        Using Google Cloud Application Default Credentials (ADC) for authentication.
        """
        # Ensure that project is set from environment or falls back gracefully
        self.project_id: str = os.getenv("GCP_PROJECT", "mediadna-test")
        self.location: str = os.getenv("GCP_LOCATION", "us-central1")
        
        # Initialize Vertex AI SDK
        aiplatform.init(project=self.project_id, location=self.location)

    async def analyze_media(self, content: str) -> BeatSheet:
        """Analyze unstructured media content (such as a script or transcript).

        Leverages Gemini 1.5 Pro with structured outputs to return a robust BeatSheet.

        Args:
            content: The unstructured string representing the script or transcript.

        Returns:
            A populated BeatSheet model.
        """
        # Let's import generative models dynamically inside to avoid unnecessary global overhead during testing
        from vertexai.generative_models import (
            GenerationConfig,
            GenerativeModel,
        )

        prompt: str = (
            "You are a master cinema deconstructor and media analyst. "
            "Analyze the following script/transcript. "
            "Extract the hooks, pacing profile, and chronological key events according to the requested JSON schema.\n\n"
            f"Content:\n{content}"
        )

        # Initialize the Gemini 1.5 Pro model
        model = GenerativeModel("gemini-1.5-pro")

        # Configure structured output to return exact JSON matching BeatSheet schema
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "hook_analysis": {"type": "STRING", "description": "Analysis of the hook used to capture viewer attention"},
                    "pacing_curve": {
                        "type": "ARRAY",
                        "items": {"type": "STRING"},
                        "description": "List of pacing descriptors (e.g., 'fast', 'climax', 'slow build')",
                    },
                    "key_events": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "timestamp": {"type": "STRING", "description": "Timestamp of the event (e.g. '0:15' or '00:02:30')"},
                                "event_description": {"type": "STRING", "description": "Detailed description of what happens at this timestamp"},
                            },
                            "required": ["timestamp", "event_description"],
                        },
                    },
                },
                "required": ["hook_analysis", "pacing_curve", "key_events"],
            },
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
        )

        response_dict: dict[str, Any] = json.loads(response.text)
        return BeatSheet.model_validate(response_dict)
