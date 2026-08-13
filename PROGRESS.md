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
