# ADR 0008: Deconstructor API Contract and Multimodal Beat Sheet Extraction

## Status
Accepted

## Context
Requests to `/api/v1/deconstruct` failed with schema validation errors (missing `content` field) and unhandled downstream exceptions. The API contract between the Streamlit UI, FastAPI router, and the Gemini-powered Deconstructor Agent must be explicitly unified to accept reference media inputs (URLs, transcripts, or uploaded video pointers) and output a strongly typed `BeatSheet`.

## Decision
1. **Request Schema**: Define `DeconstructRequest` with optional `reference_url` and optional `transcript`, requiring at least one input field.
2. **Response Schema**: Enforce `BeatSheet` with explicit `BeatItem` objects detailing timestamps, hook types, visual cues, audio cues, emotional shifts, and retention drivers.
3. **Agent Integration**: Standardize `DeconstructorAgent` on Vertex AI `gemini-1.5-pro` using structured JSON output (`response_mime_type="application/json"`).
4. **Resilience**: Add fallback string sanitization to strip leading/trailing Markdown code blocks (` ```json `) prior to Pydantic parsing.

## Consequences
- **Pros**:
  - Eliminates FastAPI HTTP 422/500 schema validation errors.
  - Ensures clean handoff of structured Beat Sheets to ClickHouse MCP storage and The Architect agent.
- **Cons**:
  - Any future change to the Beat Sheet contract requires simultaneous updates to backend models and the Streamlit renderer.