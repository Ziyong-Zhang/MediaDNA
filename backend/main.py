from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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


@app.get("/health")
async def health_check() -> HealthResponse:
    """Check the health status of the backend service."""
    return HealthResponse(status="ok", service="MediaDNA Backend", version="0.1.0")
