import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

from backend.schemas.beat_sheet import BeatSheet

logger = logging.getLogger(__name__)


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
        self.project_id: str = os.getenv("GCP_PROJECT", "media-dna-505118")
        self.location: str = os.getenv("GCP_LOCATION", "us-central1")
        self.client = genai.Client(enterprise=True, project=self.project_id, location=self.location)

    async def extract_beat_sheet(self, text_content: str, media_path: Path | None = None) -> BeatSheet:
        """Extract a structured beat sheet from text and optional multimodal media using inline bytes."""
        prompt = (
            "You are a master cinema deconstructor and media analyst. "
            "Analyze the following reference media and extract a detailed beat sheet. "
            "For each beat, identify the hook type, visual cue, audio cue, emotional shift, and retention driver. "
            "Also provide overall pacing score, viral potential summary, hooks, pacing curve, and key events. "
            "Return valid JSON strictly matching the schema below.\n\n"
            f"{text_content}"
        )

        # Assemble the multimodal payload using Inline Bytes
        contents: list[Any] = []
        if media_path is not None and media_path.exists():
            # Offload blocking file I/O to a separate thread
            media_bytes = await asyncio.to_thread(media_path.read_bytes)
            
            # Create an inline Part object. (.m4a maps to audio/mp4)
            audio_part = types.Part.from_bytes(
                data=media_bytes,
                mime_type="audio/mp4",
            )
            contents.append(audio_part)
            logger.info(f"Appended inline media bytes to prompt from: {media_path.name}")

        contents.append(prompt)

        # Direct call without try...finally because there is no remote state to clean up
        response = await self.client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
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
            ),
        )
        
        response_text = response.text or ""
        cleaned_json = sanitize_json(response_text)
        response_dict: dict[str, Any] = json.loads(cleaned_json)
        return BeatSheet.model_validate(response_dict)
    async def analyze_media(self, content: str) -> BeatSheet:
        """Deprecated: Use extract_beat_sheet instead.
        
        Analyze unstructured media content for backward compatibility.
        """
        return await self.extract_beat_sheet(text_content=content)
