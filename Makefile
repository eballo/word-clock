.PHONY: clean format test run-api

PYCACHE_DIRS := $(shell find . -type d -name "__pycache__")

clean:
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf .pytest_cache .coverage

format:
	uv run ruff format .

test:
	uv run pytest

run-api:
	uv run wordclock-api
