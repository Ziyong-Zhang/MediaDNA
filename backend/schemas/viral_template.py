from pydantic import BaseModel, Field


class ViralTemplate(BaseModel):
    """Schema for a viral content structure template stored in ClickHouse Cloud."""

    pattern_id: str = Field(..., description="Unique identifier of the viral pattern")
    pattern_type: str = Field(..., description="Category of the pattern (e.g. 'hook', 'pacing', 'twist')")
    description: str = Field(..., description="Human-readable description of the structural pattern")
    source_ref: str = Field(..., description="Reference to the source media this pattern was derived from")
