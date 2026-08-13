from pydantic import BaseModel, Field


class TTSLine(BaseModel):
    """Schema for a single narration/dialogue line in the TTS script."""

    speaker: str = Field(..., description="Name or role of the speaker delivering this line")
    text: str = Field(..., description="The narration/dialogue text to be synthesized")
    timestamp: str = Field(..., description="Timestamp for this line (e.g. '0:15' or '00:02:30')")


class ImagePrompt(BaseModel):
    """Schema for a single Imagen 3 visual prompt tied to a scene."""

    scene_id: str = Field(..., description="Identifier of the scene this prompt corresponds to")
    prompt_text: str = Field(..., description="Imagen-3-ready visual prompt text")
    style_tags: list[str] = Field(..., description="Style descriptors to guide visual generation (e.g. 'cinematic', 'neon')")


class ProductionAssets(BaseModel):
    """Strict data contract schema for the Director agent's output."""

    tts_script: list[TTSLine] = Field(..., description="Ordered narration/dialogue lines for TTS synthesis")
    visual_prompts: list[ImagePrompt] = Field(..., description="Per-scene Imagen 3 visual prompts")
    metadata: dict[str, str] = Field(..., description="Free-form production metadata (e.g. estimated duration, target platform)")
