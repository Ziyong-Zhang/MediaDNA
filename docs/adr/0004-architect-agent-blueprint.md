# ADR 0004: Architect Agent & Blueprint Schema

## Status
Accepted

## Context
The Deconstructor (F02) produces a `BeatSheet` describing the structure of a reference video. The Architect is the second agent in the multi-agent topology (see `docs/ARCHITECTURE.md`): it must take that `BeatSheet`, a user-supplied creative brief, and proven viral structure patterns (fetched via the F03 ClickHouse MCP `get_viral_templates` tool) and produce a plan for the new production that keeps what makes the reference structure work while allowing deliberate creative deviation. This plan must be a strict, typed contract so the Director (F05) can consume it without re-parsing free text.

## Decision
We define a `Blueprint` Pydantic v2 model (`backend/schemas/blueprint.py`) and an `ArchitectAgent` (`backend/agents/architect.py`) that mirrors the exact pattern already established by `DeconstructorAgent`:
- ADC-based init via `aiplatform.init(project=..., location=...)`.
- Dynamic import of `vertexai.generative_models.{GenerativeModel, GenerationConfig}` inside the analysis method (kept out of module import time for testability).
- Gemini 1.5 Pro with `response_mime_type="application/json"` and an explicit `response_schema` matching `Blueprint`, enforcing structured output instead of free-text parsing.
- Before prompting Gemini, the agent calls `backend.mcp.client.fetch_viral_templates(...)` in-process to gather `ViralTemplate` context — the Architect is the first agent to exercise the F03 MCP wiring, keeping ClickHouse access routed exclusively through MCP per the project's strict decoupling constraint.
- A `POST /api/v1/architect` FastAPI route accepts `{ beat_sheet: BeatSheet, creative_brief: str }` and returns a `Blueprint`, following the same route shape as `/api/v1/deconstruct`.

## Schema Specification
`Blueprint` contains:
- `adapted_beat_sheet` (`BeatSheet`): the reference beat sheet re-expressed for the new production (same shape, adapted content).
- `structural_alignment_notes` (list of strings): explanations of which reference structural patterns were preserved and why.
- `creative_deviations` (list of strings): explicit call-outs of where and why the new plan intentionally departs from the reference structure to honor the user's creative brief.

## Consequences
- **Type Safety**: `mypy --strict` fully type-checks the Architect exactly as it does the Deconstructor.
- **Testability**: Reuses the established mocking pattern (`aiplatform.init`, `GenerativeModel`, `GenerationConfig`) plus a mock of `fetch_viral_templates`, so `tests/test_architect.py` never makes live GCP or ClickHouse calls.
- **Decoupling**: The Architect never queries ClickHouse directly — it only calls the MCP-backed `fetch_viral_templates` wrapper, preserving the F03 data-layer boundary.
- **Downstream Compatibility**: `Blueprint` is the sole input contract for the Director (F05), so its fields are additive-only going forward to avoid breaking that consumer.
