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
- **State**: todo

## F02.1: Beat Sheet Pydantic Schema
- **Behavior**: Define a strict Pydantic v2 schema (`BeatSheet`) in `backend/schemas/beat_sheet.py` capturing hook, pacing, and key events.
- **State**: todo

## F02.2: Native ADK Agent Initialization
- **Behavior**: Create `backend/agents/deconstructor.py` wrapping Gemini 1.5 Pro via ADK. Enforce JSON output matching the Pydantic schema using structured outputs.
- **State**: todo

## F02.3: Deconstruct API Endpoint
- **Behavior**: Add `POST /api/v1/deconstruct` in FastAPI to route incoming text/media to The Deconstructor and return the parsed JSON.
- **State**: todo

## F03: Data Layer Gateway (ClickHouse MCP)
- **Behavior**: Build an MCP (Model Context Protocol) server to securely query ClickHouse Cloud using standard HTTP/HTTPS without exposing raw DB connections to the agent logic.
- **Verification**: `pytest tests/test_mcp.py` (with httpx mock).
- **State**: todo

## F03.1: MCP Server Initialization
- **Behavior**: Setup the basic MCP server skeleton in `backend/mcp/server.py` following the official Python MCP SDK.
- **State**: todo

## F03.2: ClickHouse HTTP Client & Tool Definition
- **Behavior**: Define a `get_viral_templates` tool. Implement lightweight HTTP requests to ClickHouse using environment variables (no hardcoded credentials).
- **State**: todo

## F03.3: Agent-MCP Wiring (Mocked)
- **Behavior**: Ensure the FastAPI backend can load the local MCP tools and expose them to the Native ADK Agent Engine.
- **State**: todo