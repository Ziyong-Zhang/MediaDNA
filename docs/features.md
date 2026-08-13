# Feature Tracking (WIP=1)

## F01: Core Infrastructure & Validation
- **Behavior**: Set up Python dependencies, ensure GCP ADC works, and pass a dummy pytest.
- **Verification**: `make setup && make auth && make check`
- **State**: passing
- **Evidence**: README.md and docs/ARCHITECTURE.md created. `make check` passed.

## F01.1: FastAPI Application Shell
- **Behavior**: Robust FastAPI setup in `backend/` with health check, CORS, and structural routing placeholders.
- **Verification**: `pytest tests/test_backend.py`
- **State**: passing

## F01.2: Streamlit Frontend Shell
- **Behavior**: Streamlit interface in `frontend/` with sidebar, navigation skeleton, and backend health connector.
- **Verification**: `uv run streamlit run frontend/app.py --server.headless=true` (Dry run)
- **State**: passing

## F01.3: End-to-End Shell Orchestration
- **Behavior**: Verify UI-to-API connectivity and passing complete project-wide validation.
- **Verification**: `make check`
- **State**: passing

## F02: Agent Topology (The Deconstructor)
- **Behavior**: Implement the first multimodal agent using Native GCP ADK (`LangchainAgent`) and Gemini 1.5 Pro to parse media and output a structured JSON Beat Sheet.
- **Verification**: `pytest tests/test_agents.py` (with mocked Gemini response).
- **State**: passing

## F02.1: Beat Sheet Pydantic Schema
- **Behavior**: Define a strict Pydantic v2 schema (`BeatSheet`) in `backend/schemas/beat_sheet.py` capturing hook, pacing, and key events.
- **State**: passing

## F02.2: Native ADK Agent Initialization
- **Behavior**: Create `backend/agents/deconstructor.py` wrapping Gemini 1.5 Pro via ADK. Enforce JSON output matching the Pydantic schema using structured outputs.
- **State**: passing

## F02.3: Deconstruct API Endpoint
- **Behavior**: Add `POST /api/v1/deconstruct` in FastAPI to route incoming text/media to The Deconstructor and return the parsed JSON.
- **State**: passing

## F03: Data Layer Gateway (ClickHouse MCP)
- **Behavior**: Build a self-hosted MCP (Model Context Protocol) server exposing ClickHouse Cloud viral-pattern data as tools, so agents query data only via MCP (never raw SQL/ORM in agent code), per the strict decoupling constraint.
- **Process**: Self-built lightweight `mcp` SDK server + `httpx` ClickHouse HTTP client (not the official `mcp-clickhouse` package), split across F03.1-F03.3 below.
- **Verification**: `pytest tests/test_mcp.py` (with httpx mock, no live ClickHouse calls).
- **State**: passing
- **Prerequisite**: F02 passing (done). ClickHouse Cloud instance provisioned externally with a `viral_templates` table; credentials available via env vars (`CLICKHOUSE_HOST`, `CLICKHOUSE_PORT`, `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`, `CLICKHOUSE_SECURE`) — see `.env.example`.
- **Evidence**: `backend/mcp/{server,clickhouse_client,client}.py` implemented; `tests/test_mcp.py` (5 tests) and `make check` pass cleanly.

## F03.1: MCP Server Initialization
- **Behavior**: Minimal MCP server process exposing a tool registry, following the official Python `mcp` SDK.
- **Process**: Add `mcp` package to `pyproject.toml` dependencies. Create `backend/mcp/__init__.py` and `backend/mcp/server.py` defining a server instance (e.g. `FastMCP("mediadna-clickhouse")`) with stdio transport for local dev/testing (no SSE/HTTP transport needed for hackathon scope).
- **Test**: `tests/test_mcp.py::test_server_initializes` — import the server module, assert the tool registry is constructed without raising, no network calls.
- **State**: passing
- **Prerequisite**: None beyond F02.

## F03.2: ClickHouse HTTP Client & Tool Definition
- **Behavior**: A `get_viral_templates` MCP tool that queries ClickHouse Cloud over its HTTP interface and returns structured rows, with no hardcoded credentials.
- **Process**: Create `backend/schemas/viral_template.py` (Pydantic `ViralTemplate` model). Create `backend/mcp/clickhouse_client.py` using `httpx.AsyncClient` against ClickHouse's HTTP query endpoint, reading credentials from env vars and raising a clear error (not a crash) if unset. Register `get_viral_templates(pattern_type: str | None, limit: int)` as a tool on the F03.1 server instance, parsing HTTP JSON rows into `ViralTemplate` objects.
- **Test**: `tests/test_mcp.py::test_get_viral_templates_tool` — mock `httpx.AsyncClient` to return canned JSON rows, assert the tool returns `ViralTemplate` objects; plus a test for the missing-env-var error path.
- **State**: passing
- **Prerequisite**: F03.1 server skeleton exists; `ViralTemplate` schema defined.

## F03.3: Agent-MCP Wiring (Mocked)
- **Behavior**: Backend application/agent code can invoke the MCP tool in-process, so the Architect agent (F04) can use it as a context source without leaking MCP transport details into agent logic.
- **Process**: Add `backend/mcp/client.py` exposing `async def fetch_viral_templates(...) -> list[ViralTemplate]` that calls the F03.2 tool function directly (in-process call, not a stdio subprocess round-trip — chosen for hackathon time constraints).
- **Test**: `tests/test_mcp.py::test_agent_can_fetch_templates_mocked` — mock the ClickHouse HTTP layer, call the wrapper directly, assert it returns plain `ViralTemplate` objects.
- **State**: passing
- **Prerequisite**: F03.1, F03.2 passing.

## F04: Agent Topology (The Architect)
- **Behavior**: Takes the Deconstructor's `BeatSheet` + user creative constraints + relevant `ViralTemplate`s (via F03 MCP tool) and produces a `Blueprint` — a structural plan for the new production that preserves proven structure while allowing creative deviation.
- **Verification**: `pytest tests/test_architect.py` (mocked Gemini + mocked MCP fetch).
- **State**: passing
- **Prerequisite**: F02 (BeatSheet schema + Deconstructor pattern to reuse), F03.3 (MCP wiring so the Architect can fetch templates).
- **Evidence**: `docs/adr/0004-architect-agent-blueprint.md`, `backend/schemas/blueprint.py`, `backend/agents/architect.py`, `POST /api/v1/architect` in `backend/main.py`; `tests/test_architect.py` and `make check` pass cleanly.

## F04.1: Blueprint Pydantic Schema
- **Behavior**: Strict Pydantic v2 schema capturing the mapping between the reference structure and the new creative brief.
- **Process**: Create `backend/schemas/blueprint.py` with a `Blueprint` model (e.g. `adapted_beat_sheet: BeatSheet`, `structural_alignment_notes: list[str]`, `creative_deviations: list[str]`), following the same rigor as `BeatSheet`.
- **Test**: Schema validation round-trip test (construct + serialize + parse) in `tests/test_architect.py` or a dedicated schema test.
- **State**: passing
- **Prerequisite**: `BeatSheet` schema (F02.1, done), `ViralTemplate` schema (F03.2).

## F04.2: Native ADK Architect Agent
- **Behavior**: Gemini-backed agent producing a `Blueprint` from `BeatSheet` + creative brief + templates, enforcing structured JSON output exactly like `DeconstructorAgent`.
- **Process**: Create `backend/agents/architect.py` mirroring `backend/agents/deconstructor.py` (ADC init via `aiplatform.init`, dynamic import of `GenerativeModel`/`GenerationConfig`, `response_schema` matching `Blueprint`). `async def align_structure(beat_sheet: BeatSheet, creative_brief: str) -> Blueprint` internally calls the F03.3 `fetch_viral_templates` wrapper for context before prompting Gemini.
- **Test**: `tests/test_architect.py` — same mocking pattern as `test_deconstructor.py` (mock `aiplatform.init`, `GenerativeModel`, and the MCP fetch wrapper).
- **State**: passing
- **Prerequisite**: F04.1, F03.3.

## F04.3: Architect API Endpoint
- **Behavior**: Expose the Architect over FastAPI so downstream consumers and integration tests can call it.
- **Process**: Add `POST /api/v1/architect` in `backend/main.py` accepting `{ beat_sheet: BeatSheet, creative_brief: str }`, instantiate `ArchitectAgent`, return `Blueprint`, following the exact pattern of `/api/v1/deconstruct`.
- **Test**: Extend `tests/test_architect.py` with a `TestClient` call to `POST /api/v1/architect`, mocked dependencies, asserting 200 + schema match.
- **State**: passing
- **Prerequisite**: F04.2.

## F05: Agent Topology (The Director)
- **Behavior**: Transforms a `Blueprint` into tangible production assets — TTS script and Imagen 3 visual prompts, plus production metadata. Actual TTS audio synthesis / Imagen 3 image generation calls are OUT of scope; only structured prompt/script text generation is produced.
- **Verification**: `pytest tests/test_director.py` (mocked Gemini, no live TTS/Imagen calls).
- **State**: todo
- **Prerequisite**: F04 (Blueprint schema + Architect producing it).

## F05.1: Production Asset Pydantic Schema
- **Behavior**: Strict schema for the final deliverables handed to production tooling.
- **Process**: Create `backend/schemas/production_assets.py` with a `ProductionAssets` model (e.g. `tts_script: list[TTSLine{speaker, text, timestamp}]`, `visual_prompts: list[ImagePrompt{scene_id, prompt_text, style_tags: list[str]}]`, `metadata: dict[str, str]`).
- **Test**: Schema validation round-trip test, same convention as F04.1.
- **State**: todo
- **Prerequisite**: F04.1 (`Blueprint` schema to consume as input).

## F05.2: Native ADK Director Agent
- **Behavior**: Gemini-backed agent producing `ProductionAssets` from a `Blueprint`, enforcing structured JSON output.
- **Process**: Create `backend/agents/director.py` mirroring the `deconstructor.py`/`architect.py` pattern; `async def produce_assets(blueprint: Blueprint) -> ProductionAssets`.
- **Test**: `tests/test_director.py` — same mocked-Gemini pattern as existing agent tests.
- **State**: todo
- **Prerequisite**: F05.1, F04 (Architect producing Blueprint).

## F05.3: Produce API Endpoint
- **Behavior**: Expose the Director over FastAPI.
- **Process**: Add `POST /api/v1/produce` in `backend/main.py` accepting `Blueprint`, returning `ProductionAssets`, same pattern as the other two routes.
- **Test**: Extend `tests/test_director.py` with a `TestClient` call, mocked dependencies.
- **State**: todo
- **Prerequisite**: F05.2.