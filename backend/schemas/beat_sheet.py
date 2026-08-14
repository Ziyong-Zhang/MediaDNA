from pydantic import BaseModel, Field, model_validator


class DeconstructRequest(BaseModel):
    """Schema for media deconstruction request."""

    reference_url: str | None = Field(None, description="URL to reference video/audio media")
    transcript: str | None = Field(None, description="Raw transcript or script text")

    @model_validator(mode="after")
    def check_at_least_one_source(self) -> "DeconstructRequest":
        """Ensure at least one source is provided."""
        if not self.reference_url and not self.transcript:
            raise ValueError("Either reference_url or transcript must be provided.")
        return self


class BeatItem(BaseModel):
    """Schema for a single beat in the beat sheet."""

    timestamp_sec: int = Field(..., description="Timestamp in seconds")
    hook_type: str = Field(..., description="Type of hook (e.g., 'Visual Cliffhanger', 'Audio Surprise')")
    visual_cue: str = Field(..., description="Visual element description for this beat")
    audio_cue: str = Field(..., description="Audio element description for this beat")
    emotion_shift: str = Field(..., description="Emotional shift at this beat (e.g., 'Anticipation', 'Relief')")
    retention_driver: str = Field(..., description="What drives viewer retention at this moment (e.g., 'Open Loop', 'Social Proof')")


class KeyEvent(BaseModel):
    """Schema for a single key event in the beat sheet."""

    timestamp: str = Field(..., description="Timestamp of the event (e.g. '0:15' or '00:02:30')")
    event_description: str = Field(..., description="Detailed description of what happens at this timestamp")


class BeatSheet(BaseModel):
    """Strict data contract schema for the Deconstructor agent's output."""

    title: str = Field(..., description="Title or name of the analyzed content")
    total_duration: int = Field(..., description="Total duration in seconds")
    pacing_score: float = Field(..., description="Overall pacing score (0.0 to 10.0)")
    beats: list[BeatItem] = Field(..., description="Detailed list of beats with hooks and emotional shifts")
    viral_summary: str = Field(..., description="Summary of viral potential and key retention drivers")
    # Kept for backward compatibility
    hook_analysis: str = Field(..., description="Analysis of the hook used to capture viewer attention")
    pacing_curve: list[str] = Field(..., description="List of pacing descriptors (e.g., 'fast', 'climax', 'slow build')")
    key_events: list[KeyEvent] = Field(..., description="Timeline list of key narrative or structural events")
