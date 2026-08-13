.PHONY: setup auth test lint check run-backend run-frontend

setup:
	uv sync --no-install-project --quiet

auth:
	gcloud auth application-default login --project media-dna-505118

test:
	PYTHONPATH=. uv run pytest tests/ -q

lint:
	uv run ruff check . --quiet
	uv run mypy . --strict

check: lint test

run-backend:
	PYTHONPATH=. uv run uvicorn backend.main:app --reload --port 8000

run-frontend:
	PYTHONPATH=. uv run streamlit run frontend/app.py