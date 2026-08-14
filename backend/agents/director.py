import json
import os
from typing import Any

from google import genai
from google.genai import types

from backend.schemas.blueprint import Blueprint
from backend.schemas.production_assets import ProductionAssets

_TTS_LINE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "speaker": {"type": "STRING", "description": "Name or role of the speaker delivering this line"},
        "text": {"type": "STRING", "description": "The narration/dialogue text to be synthesized"},
        "timestamp": {"type": "STRING", "description": "Timestamp for this line (e.g. '0:15' or '00:02:30')"},
    },
    "required": ["speaker", "text", "timestamp"],
}

_IMAGE_PROMPT_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "scene_id": {"type": "STRING", "description": "Identifier of the scene this prompt corresponds to"},
        "prompt_text": {"type": "STRING", "description": "Imagen-3-ready visual prompt text"},
        "style_tags": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["scene_id", "prompt_text", "style_tags"],
}


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
                        "tts_script": {"type": "ARRAY", "items": _TTS_LINE_SCHEMA},
                        "visual_prompts": {"type": "ARRAY", "items": _IMAGE_PROMPT_SCHEMA},
                        "metadata": {"type": "OBJECT"},
                    },
                    "required": ["tts_script", "visual_prompts", "metadata"],
                },
            ),
        )

        response_text = response.text or ""
        response_dict: dict[str, Any] = json.loads(response_text)
        return ProductionAssets.model_validate(response_dict)
