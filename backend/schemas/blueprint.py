from pydantic import BaseModel, Field

from backend.schemas.beat_sheet import BeatSheet


class Blueprint(BaseModel):
    """Strict data contract schema for the Architect agent's output."""

    adapted_beat_sheet: BeatSheet = Field(..., description="The reference beat sheet re-expressed for the new production")
    structural_alignment_notes: list[str] = Field(
        ..., description="Explanations of which reference structural patterns were preserved and why"
    )
    creative_deviations: list[str] = Field(
        ..., description="Explicit call-outs of where and why the plan intentionally departs from the reference structure"
    )
