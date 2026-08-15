import json
import os
from typing import Any

from google import genai
from google.genai import types

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

_BEAT_ITEM_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "timestamp_sec": {"type": "INTEGER", "description": "Timestamp in seconds"},
        "hook_type": {"type": "STRING", "description": "Type of hook (e.g., 'Visual Cliffhanger')"},
        "visual_cue": {"type": "STRING", "description": "Visual element description for this beat"},
        "audio_cue": {"type": "STRING", "description": "Audio element description for this beat"},
        "emotion_shift": {"type": "STRING", "description": "Emotional shift at this beat"},
        "retention_driver": {"type": "STRING", "description": "What drives viewer retention at this moment"},
    },
    "required": ["timestamp_sec", "hook_type", "visual_cue", "audio_cue", "emotion_shift", "retention_driver"],
}

_BEAT_SHEET_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "title": {"type": "STRING", "description": "Title or name of the analyzed content"},
        "total_duration": {"type": "INTEGER", "description": "Total duration in seconds"},
        "pacing_score": {"type": "NUMBER", "description": "Overall pacing score (0.0 to 10.0)"},
        "beats": {
            "type": "ARRAY",
            "items": _BEAT_ITEM_SCHEMA,
            "description": "Detailed list of beats with hooks and emotional shifts"
        },
        "viral_summary": {"type": "STRING", "description": "Summary of viral potential and key retention drivers"},
        "hook_analysis": {"type": "STRING", "description": "Analysis of the hook used to capture viewer attention"},
        "pacing_curve": {
            "type": "ARRAY",
            "items": {"type": "STRING"},
            "description": "List of pacing descriptors (e.g., 'fast', 'climax', 'slow build')",
        },
        "key_events": {"type": "ARRAY", "items": _KEY_EVENT_SCHEMA},
    },
    "required": ["title", "total_duration", "pacing_score", "beats", "viral_summary", "hook_analysis", "pacing_curve", "key_events"],
}


class ArchitectAgent:
    """Architect agent for mapping a reference Beat Sheet and creative brief into a structural Blueprint."""

    def __init__(self) -> None:
        """Initialize the Architect agent.

        Using Google Cloud Application Default Credentials (ADC) for authentication.
        """
        self.project_id: str = os.getenv("GCP_PROJECT", "mediadna-test")
        self.location: str = os.getenv("GCP_LOCATION", "us-central1")
        self.client = genai.Client(enterprise=True, project=self.project_id, location=self.location)

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

        response = await self.client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
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
            ),
        )

        response_text = response.text or ""
        response_dict: dict[str, Any] = json.loads(response_text)
        return Blueprint.model_validate(response_dict)
