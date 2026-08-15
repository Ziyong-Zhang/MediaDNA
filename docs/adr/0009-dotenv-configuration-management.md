# ADR 0009: Dotenv Configuration Management

## Status
Accepted

## Context
During local development and hackathon testing, the FastAPI backend and ClickHouse MCP client failed to retrieve database credentials, resulting in a `ClickHouseConfigError`. The application was relying on `os.getenv` without a mechanism to load local `.env` files into the runtime environment.

## Decision
We will enforce the use of `python-dotenv` to explicitly load environment variables at the entry points of our application (`backend/main.py` and `backend/mcp/clickhouse_client.py`). The `load_dotenv()` function must be invoked before any other internal modules or clients are initialized.

## Consequences
- Requires `python-dotenv` as a project dependency.
- Guarantees seamless transition between local `.env` execution and cloud deployment (where variables are injected natively by GCP Cloud Run).