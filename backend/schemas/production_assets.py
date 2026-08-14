"""Data contract schema for the Director agent's output."""

from pydantic import BaseModel, Field


class TTSLine(BaseModel):
    """Schema for a single narration/dialogue line formatted for Gemini TTS."""

    speaker: str = Field(..., description="Name or role of the speaker delivering this line")
    text: str = Field(..., description="The narration/dialogue text to be synthesized")
    timestamp: str = Field(..., description="Timestamp for this line (e.g., '00:00-00:05')")
    emotion_tag: str = Field(..., description="Emotion/tone tag to guide Gemini TTS voice tuning (e.g., 'energetic', 'whisper')")


class StoryboardPanel(BaseModel):
    """Schema for a single visual storyboard panel optimized for Imagen 3."""

    scene_id: str = Field(..., description="Identifier of the scene this panel corresponds to")
    imagen_prompt: str = Field(..., description="Highly detailed VFX prompt optimized for Imagen 3 image generation")
    camera_angle: str = Field(..., description="Cinematography instruction (e.g., 'Wide shot, drone pan, cinematic lighting')")


class ProductionAssets(BaseModel):
    """Strict data contract schema for the Director agent's final output.
    
    This acts as the blueprint for the Viral Pre-Production Engine dashboard.
    """

    metadata: dict[str, str] = Field(..., description="Free-form production metadata (e.g., target platform, estimated duration)")
    pacing_curve: list[str] = Field(..., description="Chronological list of emotional or pacing shifts (e.g., ['Fast hook', 'Tension build'])")
    tts_script: list[TTSLine] = Field(..., description="Ordered narration/dialogue lines for Gemini TTS synthesis")
    storyboard_panels: list[StoryboardPanel] = Field(..., description="Per-scene visual prompts for Imagen 3")