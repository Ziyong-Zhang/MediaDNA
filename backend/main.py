from typing import Annotated

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

load_dotenv()

from backend.agents.architect import ArchitectAgent
from backend.agents.deconstructor import DeconstructorAgent
from backend.agents.director import DirectorAgent
from backend.schemas.beat_sheet import BeatSheet
from backend.schemas.blueprint import Blueprint
from backend.schemas.production_assets import ProductionAssets
from backend.services.media_service import (
    cleanup_file,
    download_youtube_audio,
    save_uploaded_file,
)

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
async def deconstruct(
    transcript: Annotated[str | None, Form()] = None,
    reference_url: Annotated[str | None, Form()] = None,
    file: Annotated[UploadFile | None, File()] = None,
) -> BeatSheet:
    """Deconstruct media (via uploaded file, reference URL, or transcript) into a structured BeatSheet."""
    agent = DeconstructorAgent()

    actual_transcript = (
        transcript
        if transcript and transcript.strip()
        else "Analyze this reference media and extract its structural Viral DNA, including the hook, pacing, and emotional shifts."
    )

    if file is not None:
        file_bytes = await file.read()
        media_path = save_uploaded_file(file_bytes, file.filename or "upload")
        try:
            return await agent.extract_beat_sheet(text_content=actual_transcript, media_path=media_path)
        finally:
            cleanup_file(media_path)

    if reference_url:
        media_path = download_youtube_audio(reference_url)
        try:
            return await agent.extract_beat_sheet(text_content=actual_transcript, media_path=media_path)
        finally:
            cleanup_file(media_path)

    return await agent.extract_beat_sheet(text_content=actual_transcript)


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

