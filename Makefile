.PHONY: setup auth test lint check

setup:
	uv sync --no-install-project --quiet

auth:
	gcloud auth application-default login --project media-dna-505118

test:
	uv run pytest tests/ -q --no-header --no-summary

lint:
	uv run ruff check . --quiet
	uv run mypy . --strict

check: lint test