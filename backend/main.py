from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.agents.architect import ArchitectAgent
from backend.agents.deconstructor import DeconstructorAgent
from backend.schemas.beat_sheet import BeatSheet
from backend.schemas.blueprint import Blueprint

app = FastAPI(title="MediaDNA Backend")

# Configure CORS for hackathon development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    """Schema for health check response."""

    status: str
    service: str
    version: str


class DeconstructRequest(BaseModel):
    """Schema for media deconstruction request."""

    content: str = Field(..., description="Unstructured transcript or script content to deconstruct")


class ArchitectRequest(BaseModel):
    """Schema for structural alignment request."""

    beat_sheet: BeatSheet = Field(..., description="The Deconstructor's structured analysis of the reference media")
    creative_brief: str = Field(..., description="The user's creative intent/constraints for the new production")


@app.get("/health")
async def health_check() -> HealthResponse:
    """Check the health status of the backend service."""
    return HealthResponse(status="ok", service="MediaDNA Backend", version="0.1.0")


@app.post("/api/v1/deconstruct", response_model=BeatSheet)
async def deconstruct_media(payload: DeconstructRequest) -> BeatSheet:
    """Deconstruct unstructured media text into a structured BeatSheet."""
    agent = DeconstructorAgent()
    return await agent.analyze_media(payload.content)


@app.post("/api/v1/architect", response_model=Blueprint)
async def align_structure(payload: ArchitectRequest) -> Blueprint:
    """Map a reference BeatSheet and creative brief onto a structural Blueprint."""
    agent = ArchitectAgent()
    return await agent.align_structure(payload.beat_sheet, payload.creative_brief)

