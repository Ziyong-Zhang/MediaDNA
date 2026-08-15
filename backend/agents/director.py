import json
import os
import re
import logging
from typing import Any

from google import genai
from google.genai import types
from fastapi import HTTPException
from pydantic import ValidationError

from backend.schemas.blueprint import Blueprint
from backend.schemas.production_assets import ProductionAssets

_TTS_LINE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "speaker": {"type": "STRING", "description": "Name or role of the speaker delivering this line"},
        "text": {"type": "STRING", "description": "The narration/dialogue text to be synthesized"},
        "timestamp": {"type": "STRING", "description": "Timestamp for this line (e.g., '00:00-00:05')"},
        "emotion_tag": {"type": "STRING", "description": "Emotion/tone tag to guide Gemini TTS voice tuning"},
    },
    "required": ["speaker", "text", "timestamp", "emotion_tag"],
}

_STORYBOARD_PANEL_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "scene_id": {"type": "STRING", "description": "Identifier of the scene this panel corresponds to"},
        "imagen_prompt": {"type": "STRING", "description": "Highly detailed VFX prompt optimized for Imagen 3"},
        "camera_angle": {"type": "STRING", "description": "Cinematography instruction (e.g., 'Wide shot, drone pan')"},
    },
    "required": ["scene_id", "imagen_prompt", "camera_angle"],
}

def sanitize_json(text: str) -> str:
    """Remove markdown code fence markers from JSON response text."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip())
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()

logger = logging.getLogger(__name__)

class DirectorAgent:
    """Director agent for transforming a Blueprint into concrete production assets."""

    def __init__(self) -> None:
        """Initialize the Director agent.

        Using Google Cloud Application Default Credentials (ADC) for authentication.
        """
        self.project_id: str = os.getenv("GCP_PROJECT", "mediadna-test")
        self.location: str = os.getenv("GCP_LOCATION", "us-central1")
        self.client = genai.Client(enterprise=True, project=self.project_id, location=self.location)

    async def produce_assets(self, blueprint: Blueprint) -> ProductionAssets:
        """Transform a structural Blueprint into a TTS script and Imagen 3 visual prompts.

        Leverages Gemini 1.5 Pro with structured outputs to return ProductionAssets.
        Note: this only generates prompt/script text; no TTS audio or Imagen 3 images
        are actually synthesized/rendered by this agent.

        Args:
            blueprint: The Architect's structural plan for the new production.

        Returns:
            A populated ProductionAssets model.
        """
        prompt: str = (
            "You are a master cinema director turning a structural blueprint into production-ready assets. "
            "Given the adapted Beat Sheet, structural alignment notes, and creative deviations below, "
            "produce a TTS narration/dialogue script and per-scene Imagen 3 visual prompts, plus production metadata.\n\n"
            f"Blueprint:\n{blueprint.model_dump_json()}"
        )

        response = await self.client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "metadata": {"type": "OBJECT", "description": "Free-form production metadata"},
                        "pacing_curve": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"},
                            "description": "Chronological list of emotional or pacing shifts"
                        },
                        "tts_script": {"type": "ARRAY", "items": _TTS_LINE_SCHEMA},
                        "storyboard_panels": {"type": "ARRAY", "items": _STORYBOARD_PANEL_SCHEMA},
                    },
                    "required": ["metadata", "pacing_curve", "tts_script", "storyboard_panels"],
                },
            ),
        )

        response_text = response.text or ""
        cleaned_json = sanitize_json(response_text)
        
        try:
            response_dict: dict[str, Any] = json.loads(cleaned_json)
            return ProductionAssets.model_validate(response_dict)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.error("❌ [DirectorAgent] LLM Output Parsing or Validation Failed!")
            logger.error(f"Raw LLM Output: {response_text}")
            logger.error(f"Error: {e}")
            raise HTTPException(
                status_code=502, 
                detail="Director Agent generated an invalid schema or invalid JSON. Please retry."
            )
