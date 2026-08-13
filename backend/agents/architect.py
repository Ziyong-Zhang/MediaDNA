import json
import os
from typing import Any

from google.cloud import aiplatform

from backend.mcp.client import fetch_viral_templates
from backend.schemas.beat_sheet import BeatSheet
from backend.schemas.blueprint import Blueprint

_KEY_EVENT_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "timestamp": {"type": "STRING", "description": "Timestamp of the event (e.g. '0:15' or '00:02:30')"},
        "event_description": {"type": "STRING", "description": "Detailed description of what happens at this timestamp"},
    },
    "required": ["timestamp", "event_description"],
}

_BEAT_SHEET_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "hook_analysis": {"type": "STRING", "description": "Analysis of the hook used to capture viewer attention"},
        "pacing_curve": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "List of pacing descriptors (e.g., 'fast', 'climax', 'slow build')",
        },
        "key_events": {"type": "ARRAY", "items": _KEY_EVENT_SCHEMA},
    },
    "required": ["hook_analysis", "pacing_curve", "key_events"],
}


class ArchitectAgent:
    """Architect agent for mapping a reference Beat Sheet and creative brief into a structural Blueprint."""

    def __init__(self) -> None:
        """Initialize the Architect agent.

        Using Google Cloud Application Default Credentials (ADC) for authentication.
        """
        self.project_id: str = os.getenv("GCP_PROJECT", "mediadna-test")
        self.location: str = os.getenv("GCP_LOCATION", "us-central1")

        aiplatform.init(project=self.project_id, location=self.location)

    async def align_structure(self, beat_sheet: BeatSheet, creative_brief: str) -> Blueprint:
        """Map a reference Beat Sheet and creative brief onto a structural Blueprint.

        Fetches proven viral structure patterns via the ClickHouse MCP tool for context,
        then leverages Gemini 1.5 Pro with structured outputs to return a Blueprint.

        Args:
            beat_sheet: The Deconstructor's structured analysis of the reference media.
            creative_brief: The user's creative intent/constraints for the new production.

        Returns:
            A populated Blueprint model.
        """
        from vertexai.generative_models import (
            GenerationConfig,
            GenerativeModel,
        )

        templates = await fetch_viral_templates()
        templates_summary = "\n".join(
            f"- [{template.pattern_type}] {template.description} (source: {template.source_ref})" for template in templates
        )

        prompt: str = (
            "You are a master cinema architect who maps proven viral structures onto new creative briefs. "
            "Given the reference Beat Sheet, the user's creative brief, and known viral structure patterns, "
            "produce an adapted Beat Sheet for the new production plus notes on what structure was preserved "
            "and where the plan deliberately deviates from the reference.\n\n"
            f"Reference Beat Sheet:\n{beat_sheet.model_dump_json()}\n\n"
            f"Creative Brief:\n{creative_brief}\n\n"
            f"Known Viral Structure Patterns:\n{templates_summary or 'None available'}"
        )

        model = GenerativeModel("gemini-1.5-pro")

        generation_config = GenerationConfig(
            response_mime_type="application/json",
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "adapted_beat_sheet": _BEAT_SHEET_SCHEMA,
                    "structural_alignment_notes": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "creative_deviations": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
                "required": ["adapted_beat_sheet", "structural_alignment_notes", "creative_deviations"],
            },
        )

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
        )

        response_dict: dict[str, Any] = json.loads(response.text)
        return Blueprint.model_validate(response_dict)
