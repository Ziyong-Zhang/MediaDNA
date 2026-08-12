from pydantic import BaseModel, Field


class KeyEvent(BaseModel):
    """Schema for a single key event in the beat sheet."""

    timestamp: str = Field(..., description="Timestamp of the event (e.g. '0:15' or '00:02:30')")
    event_description: str = Field(..., description="Detailed description of what happens at this timestamp")


class BeatSheet(BaseModel):
    """Strict data contract schema for the Deconstructor agent's output."""

    hook_analysis: str = Field(..., description="Analysis of the hook used to capture viewer attention")
    pacing_curve: list[str] = Field(..., description="List of pacing descriptors (e.g., 'fast', 'climax', 'slow build')")
    key_events: list[KeyEvent] = Field(..., description="Timeline list of key narrative or structural events")
