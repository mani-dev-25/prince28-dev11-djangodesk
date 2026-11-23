
.PHONY: up down test lint

up:
	docker compose up --build

down:
	docker compose down

test:
	uv run pytest tests/unit

lint:
	uv run ruff check .
