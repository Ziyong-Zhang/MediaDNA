# ADR 0008: Migration to Unified Google GenAI SDK

## Status
Accepted

## Context
The legacy `vertexai` SDK and its associated endpoints were fully deprecated and removed as of June 2026. This resulted in hard 404 errors during runtime execution against GCP `us-central1`. Furthermore, the project requires alignment with the latest Devpost requirements for Agentic Cinema, utilizing the `google-genai` package.

## Decision
We will migrate all agent instantiations (`DeconstructorAgent`, `ArchitectAgent`, `DirectorAgent`) to use the unified `google-genai` SDK. 
- Client initialization will strictly use `genai.Client(enterprise=True)` to route requests through the Gemini Enterprise Agent Platform.
- Model targets will be upgraded to `gemini-2.5-flash`.
- Asynchronous calls will use the `client.aio.models.generate_content` interface.

## Consequences
- Requires updating the dependency matrix (ensure `google-genai` is installed).
- Syntax for `GenerationConfig` and schema definitions will map to `google.genai.types.GenerateContentConfig`.