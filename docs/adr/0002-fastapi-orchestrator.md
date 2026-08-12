# ADR 0002: FastAPI Backend Orchestrator

## Status
Accepted

## Context
MediaDNA requires a robust, high-performance API layer to orchestrate multimodal deconstruction and creative asset generation. The backend must strictly decouple the Streamlit UI from the agent logic and the data layer (ClickHouse Cloud).

## Decision
We will use **FastAPI** as the core backend orchestrator.

### Key Technical Choices:
- **Pydantic v2**: For strict data validation and serialization using Python type hints.
- **CORS Middleware**: Configured to allow all origins during the hackathon development phase to ensure seamless UI-to-API communication.
- **Standardized Health Checks**: Implementing a strictly typed `/health` endpoint to monitor service availability.
- **Future-proofing**: The architecture is designed to host Native GCP ADK agent engines as modular routers.

## Consequences
- **Pros**: 
  - Automatic OpenAPI documentation generation.
  - Native support for asynchronous operations.
  - Strict type safety with `mypy --strict` compliance.
- **Cons**:
  - Adds an additional layer between the UI and Agents, but this is required for the project's decoupling constraints.
