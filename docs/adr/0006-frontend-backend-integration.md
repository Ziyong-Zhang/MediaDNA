# ADR 0006: Frontend-Backend Integration (Full Pipeline Wiring)

## Status
Accepted

## Context
`frontend/app.py` currently only exercises `GET /health`; the Deconstructor, Architect, and Director endpoints (F02.3, F04.3, F05.3) are fully implemented and passing but unreachable from the UI. To finish the hackathon demo path, the Streamlit frontend must drive the complete Deconstruct → Align → Produce pipeline while preserving the strict decoupling constraint (UI never touches agents or ClickHouse directly — every call goes through the FastAPI backend).

This feature also formalizes a stricter verification requirement (see `docs/features.md` "Verification Policy"): every sub-task must pass a three-tier check — static analysis, actual runtime execution, and system-level/end-to-end correctness — before being marked `passing`. Prior features (F02-F05) satisfied tiers 1-2 well (ruff/mypy + mocked pytest) but had lighter tier-3 coverage; F06 is the first feature to require explicit tier-3 evidence for every sub-task.

## Decision
- Introduce `frontend/api_client.py` as the **only** module in `frontend/` allowed to make HTTP calls, isolating `requests` usage (mirrors and extends the existing `ping_backend` pattern) behind typed functions: `deconstruct()`, `architect()`, `produce()`. UI code in `app.py` calls these functions and never calls `requests` directly.
- Use `st.session_state` to carry the `BeatSheet` → `Blueprint` → `ProductionAssets` chain between the three UI sections, so each stage's output becomes the next stage's input without re-fetching or duplicating state.
- Adopt `streamlit.testing.v1.AppTest` (bundled with the installed Streamlit 1.61) for automated frontend testing — it runs the real script in-process and lets tests interact with widgets and assert on rendered output, satisfying Tier 2 without a browser.
- For Tier 3, back the mocked-Gemini FastAPI `app` with `AppTest` by monkeypatching `frontend.api_client`'s HTTP calls to route into the real FastAPI app in-process (via `fastapi.testclient.TestClient`) instead of a live socket — this keeps the test fast/deterministic while still exercising the real backend routing, Pydantic validation, and agent code paths end-to-end.
- Sub-tasks are ordered so each one is independently testable at all three tiers before the next begins (F06.1 client layer → F06.2/3/4 per-stage UI wiring → F06.5 full-pipeline end-to-end test).

## Consequences
- **Decoupling preserved**: `frontend/api_client.py` is the single seam between UI and backend; no agent/DB imports ever appear under `frontend/`.
- **Testability without a browser**: `AppTest` gives fast, deterministic frontend tests; no Selenium/Playwright dependency needed for this hackathon scope.
- **Stronger completion evidence**: every F06 sub-task requires a passing tier-3 test that runs the real FastAPI app (mocked Gemini only), so "passing" means the full click-path produces correct data, not just that widgets render.
- **Follow-on tests**: The existing `tests/test_backend.py`, `test_deconstructor.py`, `test_architect.py`, `test_director.py` remain tier-2 evidence for the backend; F06 tests live in `tests/test_frontend_*.py` and are additive.
