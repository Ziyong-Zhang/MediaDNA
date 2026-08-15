from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

from backend.agents.architect import ArchitectAgent
from backend.agents.deconstructor import DeconstructorAgent
from backend.agents.director import DirectorAgent
from backend.schemas.beat_sheet import BeatSheet, DeconstructRequest
from backend.schemas.blueprint import Blueprint
from backend.schemas.production_assets import ProductionAssets

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
    """Deconstruct media (via reference URL or transcript) into a structured BeatSheet."""
    agent = DeconstructorAgent()
    return await agent.extract_beat_sheet(reference_url=payload.reference_url, transcript=payload.transcript)


@app.post("/api/v1/architect", response_model=Blueprint)
async def align_structure(payload: ArchitectRequest) -> Blueprint:
    """Map a reference BeatSheet and creative brief onto a structural Blueprint."""
    agent = ArchitectAgent()
    return await agent.align_structure(payload.beat_sheet, payload.creative_brief)


@app.post("/api/v1/produce", response_model=ProductionAssets)
async def produce_assets(payload: Blueprint) -> ProductionAssets:
    """Transform a structural Blueprint into TTS script and Imagen 3 visual prompt assets."""
    agent = DirectorAgent()
    return await agent.produce_assets(payload)

