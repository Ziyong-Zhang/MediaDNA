## [2026-08-15] - Subtask F10.3 Completed: Streamlit Multimodal UI & API Seam Wiring
- **Achievement**: Implemented the Hybrid Multipart Mode (per ADR-0010-3) wiring the Streamlit frontend to the FastAPI backend for both YouTube URLs and raw media uploads.
- **Backend**: Refactored `POST /api/v1/deconstruct` in `backend/main.py` to use `Annotated[..., Form()]` + `Annotated[UploadFile|None, File()]`, replacing the old Pydantic JSON body. Uploaded files are persisted via `save_uploaded_file` and YouTube URLs via `download_youtube_audio`, with strict `finally`/`try/finally` cleanup of temp files after extraction.
- **Frontend**: Updated `frontend/api_client.deconstruct()` to dynamically send `requests.post` multipart payloads (`data=` + `files=` for uploads, `data=` with `reference_url` for URLs). Added `st.tabs(["YouTube URL", "Upload File"])` with `st.text_input` and `st.file_uploader` in `frontend/app.py`, and wired the "Run Full Pipeline" button to pass either `reference_url` or `file_bytes`/`file_name`.
- **Tests**: Updated `tests/test_deconstructor.py`, `tests/test_frontend_api_client.py`, and `tests/test_frontend_ui.py` to use `data=`/`files=` instead of `json=`, with new coverage for file upload cleanup, YouTube URL download cleanup, and the tabbed UI rendering.
- **Quality**: Verified `32 passed, 1 skipped` on `pytest tests/`, plus clean `ruff check . --fix` and `mypy . --strict`. F10.3 marked `passing` in `docs/features.md`.

## [2026-08-15] - Subtask F10.2 Completed: Gemini File API & Multimodal Beat Sheet Extraction
- **Achievement**: Upgraded `DeconstructorAgent` to process multimodal media via inline bytes (`types.Part.from_bytes`) instead of remote File API, complying with Vertex AI Enterprise SDK requirements.
- **Architectural Shift**: Achieved absolute Zero-Retention security by bypassing GCP cloud storage entirely and processing lightweight media directly in memory.
- **Verification**: Built and verified unit tests (`tests/test_deconstructor.py`) and a permanent live integration test (`tests/test_live_multimodal.py`).
- **Quality**: Verified 100% clean passes on `pytest -m live`, `ruff check`, and `mypy --strict`.

## [2026-08-15] - Subtask F10.1 Completed: Media Ingestion & Audio Extraction Service
- **Achievement**: Implemented `backend/services/media_service.py` with robust support for YouTube audio download via `yt-dlp` and raw upload file handling.
- **Safety Limits**: Enforced 10-minute video duration cap throwing `ValueError` and security considerations for filename path traversal.
- **Verification**: Built and verified unit tests (`tests/test_media_service.py`) mocking `yt_dlp.YoutubeDL`.
- **Quality**: Verified 100% clean passes on both `pytest tests/test_media_service.py` and project-wide `make check` (ruff lint and mypy --strict typing validation).

## [2026-08-15] - F09 Execution: Live E2E Pipeline Unlocked & ADR-0010
- **Achievement**: Successfully executed the full Deconstruct → Architect → Produce pipeline using live Gemini 2.5 Flash models via the Google GenAI SDK.
- **Critical Fix**: Resolved a `400 INVALID_ARGUMENT` pre-flight schema validation error in the Director agent caused by a duplicate `required` dictionary key in the API payload.
- **Resilience Added**: Added `sanitize_json` (stripping Markdown fences) and Pydantic `ValidationError` boundaries (returning HTTP 502) across all ADK agents to gracefully handle live LLM hallucinations and avoid unhandled FastAPI 500 crashes.
- **Current State**: The backend and agent topology are production-ready. The Streamlit UI successfully receives and renders the `ProductionAssets` payload from live GCP calls.

## [2026-08-14] - ADR 0009: Dotenv Configuration Management

### Configuration Fix Applied
- Added `load_dotenv()` at the backend entry points so local `.env` values are loaded before internal clients initialize.
- This was implemented in `backend/main.py` and `backend/mcp/clickhouse_client.py` to fix missing ClickHouse credential failures during local development.
- The project now follows the ADR requirement that `.env` values be loaded explicitly at runtime while remaining compatible with GCP Cloud Run environment injection.

---

## [2026-08-14] - F07 + F08 Execution: ClickHouse Verified & Viral Pre-Production Dashboard

### F07 Completed: ClickHouse Data Layer Verified Live
- Ran live integration tests with `CLICKHOUSE_LIVE_TEST=true pytest tests/test_mcp_live.py` against real ClickHouse Cloud instance.
- **Test Result**: `test_fetch_viral_templates_live` PASSED — confirms that `backend/mcp/client.py::fetch_viral_templates()` successfully queries a real ClickHouse database and parses responses into `ViralTemplate` objects.
- Marked F07, F07.1, F07.2, F07.3 as `passing` in `docs/features.md`. The database schema initialization (`backend/db/init_db.py`), data seeding (`backend/db/seed.py`), and live MCP integration are all verified and production-ready.
- This clears the final blocker for live agent execution: ClickHouse MCP is now verified against real data, not mocked responses.

### F08 In-Progress: Viral Pre-Production Engine Dashboard
- **Focus**: Rewrite `frontend/app.py` as a cinematic "Viral Pre-Production Engine" dashboard showcasing Imagen 3 storyboard prompts and Gemini TTS scripts.
- **Architecture**:
  - Added sidebar toggle: `MOCK MODE (Bypass API limits)` — when True, directly inject a high-energy hiking-boots-themed `ProductionAssets` dict matching the Pydantic schema exactly (no backend calls).
  - When False: wire to real backend API via `api_client`.
  - Split-screen multi-column layout: Metadata header → Pacing Curve → Two-column (TTS Script left, Storyboard Prompts right).
- **Schema Compliance**: Mock data strictly conforms to `ProductionAssets` schema (metadata, pacing_curve, tts_script, storyboard_panels).
- **Next**: Polish UI styling, add frontend linting (ruff + mypy --strict clean), final e2e smoke test, then commit.

**Where things stand**: F07 live database verification is complete. F08 dashboard is in active development, with mock mode fully functional for offline prototyping and live-backend fallback ready once user provides credentials.

**Known gaps / blockers**:
1. `make auth` (real GCP ADC) still not exercised — agents will fail against real Vertex AI without valid credentials.
2. Live Gemini TTS / Imagen 3 calls are out of scope (text-only prompts generated).

**Next Steps**: Complete F08 polish, commit, then WIP=1 on live credential setup (`make auth`) for fully authenticated end-to-end demo.

## [2026-08-13] - F06 Execution
- Implemented `frontend/api_client.py` (F06.1): `deconstruct()`, `architect()`, `produce()`, `health()`, all raising `BackendError`; sole HTTP seam under `frontend/`.
- Rewrote `frontend/app.py` (F06.2-F06.4) to chain the three stages through `st.session_state`: Deconstructor → Architect → Director, each gated on the previous stage's output existing.
- Added `tests/conftest.py` with a shared `live_backend_url` fixture (real `uvicorn.Server` on a background thread, genuine HTTP) and a `mocked_gemini_pipeline()` context manager (mocks `aiplatform.init`, `GenerativeModel`, `GenerationConfig`, `fetch_viral_templates`, dispatching canned JSON per agent by prompt content).
- Added `tests/test_frontend_api_client.py` (Tier 2 mocked + Tier 3 live-backend), `tests/test_frontend_ui.py` (`AppTest`-driven Tier 2/3 per workflow stage), `tests/test_frontend_e2e.py` (Tier 3 full Deconstruct → Align → Produce pipeline in one `AppTest` session).
- Added `tests/__init__.py` to make `tests` a proper package so `tests.conftest` helpers can be imported and type-checked consistently by `mypy --strict`.
- `make check` passes cleanly: 19 tests total (ruff + mypy --strict clean). F06 and F06.1-F06.5 marked passing in `docs/features.md`, each with recorded Tier 1/2/3 evidence per the Three-Tier Termination Check policy.
- The full MediaDNA pipeline (Streamlit UI → FastAPI → Deconstructor/Architect/Director agents) is now wired end-to-end and verified with mocked Gemini; only live GCP credentials and a real ClickHouse `viral_templates` table remain as external, non-code prerequisites for a fully live demo.

**Next Steps**:
- No further planned features in `docs/features.md`; candidate follow-ups (not yet scoped): provision the ClickHouse `viral_templates` table for live MCP calls, wire real GCP credentials for a live demo run, and richer error/loading UX in the frontend.

## [2026-08-13] - F06 Planning
- Formalized a "Three-Tier Termination Check" verification policy in `docs/features.md` (Tier 1: ruff+mypy static analysis; Tier 2: actual runtime execution — pytest / `streamlit.testing.v1.AppTest`; Tier 3: system-level end-to-end correctness). No task may be marked `passing` without evidence at all three tiers going forward.
- Wrote `docs/adr/0006-frontend-backend-integration.md` documenting the frontend integration design before implementation: `frontend/api_client.py` as the sole HTTP seam, `st.session_state` for pipeline state, `AppTest` for Tier 2, `TestClient`-backed real backend for Tier 3.
- Planned F06 (Frontend-Backend Integration) sub-tasks in `docs/features.md`: F06.1 API client layer, F06.2/F06.3/F06.4 per-stage UI wiring (Deconstructor/Architect/Director), F06.5 full-pipeline end-to-end verification. All currently `todo`.

**Next Steps**:
- Implement F06.1: `frontend/api_client.py` + `tests/test_frontend_api_client.py` (Tier 1/2/3).
- Then F06.2 → F06.3 → F06.4 UI wiring, each gated by all three verification tiers before moving on (WIP=1).
- Finish with F06.5 full-pipeline end-to-end test.

## [2026-08-13] - F05 Execution
- Wrote `docs/adr/0005-director-agent-production-assets.md` documenting the Director agent design before implementation (explicitly scoping out real TTS/Imagen 3 calls — text-only asset generation).
- Added the `ProductionAssets` schema (`backend/schemas/production_assets.py`): `tts_script` (`TTSLine`), `visual_prompts` (`ImagePrompt`), `metadata`.
- Implemented `DirectorAgent` (`backend/agents/director.py`) mirroring the Deconstructor/Architect Gemini structured-output pattern; input is a `Blueprint` only (no MCP/ClickHouse dependency).
- Added `POST /api/v1/produce` in `backend/main.py`.
- Added `tests/test_director.py` (mocked Gemini, no live calls). `make check` passes cleanly (9 tests total). F05, F05.1, F05.2, F05.3 marked passing in `docs/features.md`.
- With F02 (Deconstructor), F04 (Architect), and F05 (Director) complete, the full Deconstruct → Align → Produce pipeline described in `docs/ARCHITECTURE.md` is implemented end-to-end (each stage independently callable via its own FastAPI route).

**Next Steps**:
- No further backend agent tasks currently planned in `docs/features.md`; next candidate work is wiring the Streamlit frontend (`frontend/app.py`) to the three real endpoints (`/api/v1/deconstruct`, `/api/v1/architect`, `/api/v1/produce`) instead of only the health check — not yet scoped as a formal feature.
- ClickHouse Cloud `viral_templates` table still needs to be provisioned/populated externally before live (non-mocked) MCP calls will work end-to-end.

## [2026-08-13] - F04 Execution
- Wrote `docs/adr/0004-architect-agent-blueprint.md` documenting the Architect agent design before implementation.
- Added the `Blueprint` schema (`backend/schemas/blueprint.py`): `adapted_beat_sheet`, `structural_alignment_notes`, `creative_deviations`.
- Implemented `ArchitectAgent` (`backend/agents/architect.py`) mirroring the Deconstructor's Gemini structured-output pattern; it calls `fetch_viral_templates()` (F03 MCP wiring) for context before prompting Gemini.
- Added `POST /api/v1/architect` in `backend/main.py`.
- Added `tests/test_architect.py` (mocked Gemini + mocked MCP fetch, no live calls). `make check` passes cleanly (8 tests total). F04, F04.1, F04.2, F04.3 marked passing in `docs/features.md`.

**Next Steps**:
- Transition to F05.1: `ProductionAssets` Pydantic schema in `backend/schemas/production_assets.py`.
- Then F05.2 (Director agent) and F05.3 (`/api/v1/produce` endpoint), reusing the same mocked-Gemini test pattern.

## [2026-08-13] - F03 Execution
- Planned F03 (ClickHouse MCP), F04 (Architect), F05 (Director) in detail in `docs/features.md` (Behavior/Process/Test/State/Prerequisite per sub-task).
- Built the self-hosted MCP server (`backend/mcp/server.py`) using the official `mcp` SDK (`MCPServer`), exposing a `get_viral_templates` tool.
- Implemented the ClickHouse Cloud HTTP client (`backend/mcp/clickhouse_client.py`) with env-var-only credentials and a clear `ClickHouseConfigError` when unset; added `ViralTemplate` schema.
- Added the in-process agent-facing wrapper (`backend/mcp/client.py::fetch_viral_templates`) so future agents avoid MCP transport/subprocess overhead.
- Added `tests/test_mcp.py` (5 tests, httpx mocked, no live ClickHouse calls). Fixed a pre-existing `mypy --strict` drift in `backend/agents/deconstructor.py` (stale `type: ignore` comments) blocking `make check`.
- `make check` passes cleanly. F03, F03.1, F03.2, F03.3 marked passing in `docs/features.md`.

**Debugging Note — `MCPServer.list_tools()` "coroutine was never awaited" / not iterable**:
- **Issue**: `server.list_tools()` raised `TypeError: 'coroutine' object is not iterable` (plus an "unawaited coroutine" warning) when called directly in a script/test.
- **Reason**: The resolved `mcp` package is SDK v2.0.0, where `FastMCP` was renamed/moved to `mcp.server.mcpserver.MCPServer`. `list_tools()` is `async` there, but the SDK's `from __future__ import annotations` makes `inspect.signature()` display a misleading non-awaitable-looking return type, making it easy to call it without `await`.
- **Solution**: Import `MCPServer` from `mcp.server.mcpserver` (not `mcp.server.fastmcp.FastMCP`, which no longer exists in v2), and always `await server.list_tools()` — wrapped in `asyncio.run(...)` in tests since the project has no `pytest-asyncio` dependency.

**Next Steps**:
- Transition to F04.1: `Blueprint` Pydantic schema in `backend/schemas/blueprint.py`.
- Then F04.2 (Architect agent) and F04.3 (`/api/v1/architect` endpoint), reusing the Deconstructor's mocked-Gemini test pattern.
- ClickHouse Cloud `viral_templates` table still needs to be provisioned/populated externally before live (non-mocked) MCP calls will work.

## [2026-08-13] - F02 Execution
- Completed the Pydantic v2 data contract (`BeatSheet`) in `backend/schemas/beat_sheet.py`, capturing hook, pacing, and key events.
- Initialized the Native ADK Agent (`LangchainAgent`) in `backend/agents/deconstructor.py`, wrapping Gemini 1.5 Pro with structured JSON output enforced against the Beat Sheet schema.
- Implemented strictly mocked `pytest` implementations to validate agent behavior without live GCP calls.

**Next Steps**:
- Transition to F03: Build the Data Layer Gateway (ClickHouse MCP).
- Set up the MCP server skeleton in `backend/mcp/server.py`.
- Define a `get_viral_templates` tool with a lightweight ClickHouse HTTP client.

## [2026-12-08] - F01 Execution
- Verified FastAPI Application Shell (F01.1) and marked it as passing.
- Developed Streamlit Frontend Shell (F01.2) in `frontend/app.py` with wide layout, title, agent modes placeholder, reference media upload / text area inputs, and backend connection test capability.
- Validated complete system-wide connectivity (F01.3) with `make check` passing 100% cleanly.
- Upgraded typing annotations and code formatting to comply with ruff and mypy.

**Next Steps**:
- Connect frontend to actual API routes.
- Integrate native GCP Vertex AI Agents (Deconstructor, Architect, Director).
- Route database queries through ClickHouse Cloud using the ClickHouse MCP.

## [2026-12-08] - F0.5 Execution
- Created professional `README.md` with project overview and architecture stack.
- Created `docs/ARCHITECTURE.md` detailing multi-agent topology (Deconstructor, Architect, Director) and MCP integration.
- Verified project state with `make check`.
- All documentation aligned with `.clinerules` and hackathon constraints.
