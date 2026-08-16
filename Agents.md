# MediaDNA - System Prompts & Core Directives

## Mission & Architecture
Build "MediaDNA" for the Agentic Cinema Hackathon.
- Frontend: Streamlit
- Backend: FastAPI + Uvicorn
- Agents: Native GCP `google-cloud-aiplatform[agent_engines,adk]>=1.101.0`
- Database: ClickHouse Cloud via Model Context Protocol (MCP)

## Absolute Constraints (CRITICAL)
1. Architecture: Strict decoupling. UI does not touch DB. Agents communicate via FastAPI.
2. Tool Subsystem: You are permitted to use shell execution for testing and linting. Database interactions MUST be routed through the ClickHouse MCP.

## Agent ACID State Management
- **Atomicity**: One feature = One Git commit. If tests fail, do not commit.
- **Consistency**: `make check` must pass entirely before transitioning a feature to `passing`.
- **Isolation**: Strictly ONE active task (WIP=1). Refer to `docs/features.md`.
- **Durability**: Always write your next steps and blockers to `PROGRESS.md` before ending a session.

## Onboarding / Commands
- Env Setup: `make setup`
- Auth: `make auth`
- Validate: `make check`

## Python Execution & Environment Rules
- **PYTHONPATH Convention**: The project relies on the root directory for module resolution. Whenever you execute tests (`pytest`), linters (`ruff`), type checkers (`mypy`), or run Python scripts via the terminal, you MUST unconditionally prefix the command with `PYTHONPATH=.`. 
- **Command Example**: Do not use `uv run pytest`, instead use `PYTHONPATH=. uv run python -m pytest tests/`.
- **Reasoning**: This prevents `ModuleNotFoundError` for internal backend packages (e.g., `backend.services...`) and avoids wasting time debugging environment paths.

## Definition of Done
- Feature complete = end-to-end verification passed, not "code is written"
- Required verification levels:
  1. Unit tests pass
  2. Integration tests pass
  3. End-to-end flow verification passes
- Do not proceed to level 2 if level 1 fails
- Do not proceed to level 3 if level 2 fails

## Session Exit Checklist
- [ ] Build passes (npm run build)
- [ ] All tests pass (npm test)
- [ ] Feature list updated
- [ ] No debug code remaining (console.log, debugger, TODO)
- [ ] Standard startup path available (npm run dev)

## Command whitelist
- `git add`
- `git commit`
