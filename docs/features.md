# Feature Tracking (WIP=1)

## F01: Core Infrastructure & Validation
- **Behavior**: Set up Python dependencies, ensure GCP ADC works, and pass a dummy pytest.
- **Verification**: `make setup && make auth && make check`
- **State**: passing
- **Evidence**: README.md and docs/ARCHITECTURE.md created. `make check` passed.

## F01.1: FastAPI Application Shell
- **Behavior**: Robust FastAPI setup in `backend/` with health check, CORS, and structural routing placeholders.
- **Verification**: `pytest tests/test_backend.py`
- **State**: active

## F01.2: Streamlit Frontend Shell
- **Behavior**: Streamlit interface in `frontend/` with sidebar, navigation skeleton, and backend health connector.
- **Verification**: `uv run streamlit run frontend/app.py --server.headless=true` (Dry run)
- **State**: pending

## F01.3: End-to-End Shell Orchestration
- **Behavior**: Verify UI-to-API connectivity and passing complete project-wide validation.
- **Verification**: `make check`
- **State**: pending
