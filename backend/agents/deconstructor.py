import json
import os
import re
from typing import Any

from google.cloud import aiplatform

from backend.schemas.beat_sheet import BeatSheet


def sanitize_json(text: str) -> str:
    """Remove markdown code fence markers from JSON response text.
    
    Handles patterns like ```json ... ``` or ``` ... ```.
    
    Args:
        text: Raw text potentially wrapped in markdown code fences
        
    Returns:
        Clean JSON string ready for parsing
    """
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


class DeconstructorAgent:
    """Deconstructor agent for extracting structured Beat Sheets from unstructured reference media."""

    def __init__(self) -> None:
        """Initialize the Deconstructor agent.
        
        Using Google Cloud Application Default Credentials (ADC) for authentication.
        """
        # Ensure that project is set from environment or falls back gracefully
        self.project_id: str = os.getenv("GCP_PROJECT", "media-dna-505118")
        self.location: str = os.getenv("GCP_LOCATION", "us-central1")
        
        # Initialize Vertex AI SDK
        aiplatform.init(project=self.project_id, location=self.location)

    async def extract_beat_sheet(
        self,
        reference_url: str | None = None,
        transcript: str | None = None,
    ) -> BeatSheet:
        """Extract structured beat sheet from reference media URL or transcript.

        Leverages Gemini 1.5 Pro with structured outputs to return a robust BeatSheet.

        Args:
            reference_url: Optional URL to reference video/audio media
            transcript: Optional raw transcript or script text

        Returns:
            A populated BeatSheet model with detailed beats and pacing analysis.
            
        Raises:
            ValueError: If neither reference_url nor transcript is provided.
        """
        if not reference_url and not transcript:
            raise ValueError("Either reference_url or transcript must be provided.")

        # Build the content description for Gemini
        content_description = ""
        if reference_url:
            content_description += f"Reference URL: {reference_url}\n"
        if transcript:
            content_description += f"Transcript:\n{transcript}"

        # Let's import generative models dynamically inside to avoid unnecessary global overhead during testing
        from vertexai.generative_models import (
            GenerationConfig,
            GenerativeModel,
        )

        prompt: str = (
            "You are a master cinema deconstructor and media analyst. "
            "Analyze the following reference media and extract a detailed beat sheet. "
            "For each beat, identify the hook type, visual cue, audio cue, emotional shift, and retention driver. "
            "Also provide overall pacing score, viral potential summary, hooks, pacing curve, and key events. "
            "Return valid JSON strictly matching the schema below.\n\n"
            f"{content_description}"
        )

        # Initialize the Gemini 1.5 Pro model
        model = GenerativeModel("gemini-1.5-pro")

        # Configure structured output to return exact JSON matching extended BeatSheet schema
        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "title": {"type": "STRING", "description": "Title or name of the analyzed content"},
                    "total_duration": {"type": "INTEGER", "description": "Total duration in seconds"},
                    "pacing_score": {"type": "NUMBER", "description": "Overall pacing score (0.0 to 10.0)"},
                    "beats": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "timestamp_sec": {"type": "INTEGER", "description": "Timestamp in seconds"},
                                "hook_type": {"type": "STRING", "description": "Type of hook"},
                                "visual_cue": {"type": "STRING", "description": "Visual element description"},
                                "audio_cue": {"type": "STRING", "description": "Audio element description"},
                                "emotion_shift": {"type": "STRING", "description": "Emotional shift at this beat"},
                                "retention_driver": {"type": "STRING", "description": "What drives viewer retention"},
                            },
                            "required": ["timestamp_sec", "hook_type", "visual_cue", "audio_cue", "emotion_shift", "retention_driver"],
                        },
                    },
                    "viral_summary": {"type": "STRING", "description": "Summary of viral potential and key retention drivers"},
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
                                "timestamp": {"type": "STRING", "description": "Timestamp of the event"},
                                "event_description": {"type": "STRING", "description": "Detailed description of what happens"},
                            },
                            "required": ["timestamp", "event_description"],
                        },
                    },
                },
                "required": ["title", "total_duration", "pacing_score", "beats", "viral_summary", "hook_analysis", "pacing_curve", "key_events"],
            },
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
        )

        # Sanitize and parse response JSON
        cleaned_json = sanitize_json(response.text)
        response_dict: dict[str, Any] = json.loads(cleaned_json)
        return BeatSheet.model_validate(response_dict)

    async def analyze_media(self, content: str) -> BeatSheet:
        """Deprecated: Use extract_beat_sheet instead.
        
        Analyze unstructured media content for backward compatibility.
        """
        return await self.extract_beat_sheet(transcript=content)
