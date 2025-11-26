.PHONY: install lint format check test serve

install:
	pip install -e .[dev]

lint:
	ruff check .

format:
	black .

check:
	black --check .
	ruff check .
	pytest

test:
	pytest

serve:
	uvicorn server.api:app --reload
