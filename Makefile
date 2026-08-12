.PHONY: setup auth test lint check

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