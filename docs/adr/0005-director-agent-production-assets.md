# ADR 0005: Director Agent & Production Assets Schema

## Status
Accepted

## Context
The Architect (F04) produces a `Blueprint` describing how the new production should be structured relative to the reference media. The Director is the third and final agent in the multi-agent topology (see `docs/ARCHITECTURE.md`): it must transform that `Blueprint` into concrete production deliverables — a TTS script and Imagen 3 visual prompts — plus production metadata, so a human or downstream tooling can act on it directly.

For this hackathon phase, actually synthesizing TTS audio or calling Imagen 3 to render images is out of scope: those are external, billable, non-deterministic calls that would complicate testing and are not required to prove the agent topology end-to-end. The Director therefore only generates the structured **text** (scripts and prompts) that would be handed to those downstream services.

## Decision
We define a `ProductionAssets` Pydantic v2 model (`backend/schemas/production_assets.py`) and a `DirectorAgent` (`backend/agents/director.py`) that mirrors the exact pattern already established by `DeconstructorAgent` and `ArchitectAgent`:
- ADC-based init via `aiplatform.init(project=..., location=...)`.
- Dynamic import of `vertexai.generative_models.{GenerativeModel, GenerationConfig}` inside the production method.
- Gemini 1.5 Pro with `response_mime_type="application/json"` and an explicit `response_schema` matching `ProductionAssets`, enforcing structured output.
- Input is a single `Blueprint` (no additional MCP/ClickHouse lookups — the Director works purely from the Architect's output).
- A `POST /api/v1/produce` FastAPI route accepts a `Blueprint` and returns `ProductionAssets`, following the same route shape as `/api/v1/deconstruct` and `/api/v1/architect`.

## Schema Specification
`ProductionAssets` contains:
- `tts_script` (list of `TTSLine`): ordered narration/dialogue lines, each with `speaker` (string), `text` (string), `timestamp` (string, matching the Beat Sheet's timestamp convention).
- `visual_prompts` (list of `ImagePrompt`): one entry per scene, each with `scene_id` (string), `prompt_text` (string, Imagen-3-ready prompt), `style_tags` (list of strings).
- `metadata` (dict of string to string): free-form production metadata (e.g. estimated duration, target platform).

## Consequences
- **Type Safety**: `mypy --strict` fully type-checks the Director exactly as it does the Deconstructor and Architect.
- **Testability**: Reuses the established mocking pattern (`aiplatform.init`, `GenerativeModel`, `GenerationConfig`); no MCP/ClickHouse mocks needed since the Director has no data-layer dependency.
- **Scope boundary**: No real TTS audio synthesis or Imagen 3 image generation happens in this phase — `ProductionAssets` is text-only. Wiring those external calls is a later stretch task, not covered by F05.
- **Pipeline completion**: With F02 (Deconstructor), F04 (Architect), and F05 (Director) all in place, the full Deconstruct → Align → Produce agent pipeline described in `docs/ARCHITECTURE.md` is implemented end-to-end (each stage independently callable via its own FastAPI route).
