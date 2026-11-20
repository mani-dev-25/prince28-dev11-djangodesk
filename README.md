# DjangoDesk

A Django expert focused on ORM performance and security, answering from the official docs with code that runs and shows the SQL it produces.

**Status:** Day 4 â€” Docker, database setup, testing, and quality gates. Live URL from Day 5.

## Who it's for

Python web developer at a Coimbatore startup whose Django admin pages became slow as data grew.

## The problem

Django's ORM lets you write Python instead of SQL, but it hides the queries it runs. If you read `order.customer.name` inside a loop, Django fires one extra query for every row. This is called an N+1 query problem. An admin page showing 500 orders can end up making 1,500 queries and nobody notices until the page becomes slow. The official docs explain the fix, but they are huge and change between versions, so finding the right answer takes time.

## Data sources

Django documentation (docs/ folder in the repo) for the last 3 LTS versions, release notes, security release notes.

- https://github.com/django/django
- https://docs.djangoproject.com/
- Terms: Django docs BSD-licensed with the code.

## Hardest problem (my interview story)

ORM to SQL: answers about N+1 queries, `select_related` vs `prefetch_related` or `annotate` must give code that runs on a sample project and show the number of SQL queries before and after.

## Signature feature

ORM to SQL viewer: every ORM answer runs against a sample database and shows the SQL and query count.

## Target metric

90%+ of ORM code answers run and reduce queries as claimed on 30 tasks.

## Run locally

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

Copy the example environment file:

```powershell
Copy-Item .env.example .env
```

Update `.env` with your database configuration.

### 3. Start the development server

```bash
uv run poe dev
```

### 4. Open API documentation

Visit:

http://localhost:8000/docs

## Docker

Make sure Docker Engine is installed and running before executing these commands.

### Build and start services

```bash
docker compose up --build
```

### Stop services

```bash
docker compose down
```

### Stop services and remove database volumes

```bash
docker compose down -v
```

> **Warning:** `docker compose down -v` removes the database volume and its stored data.

## Testing

### Run tests

```bash
uv run poe test
```

### Run integration tests

```bash
uv run poe test-integration
```

Integration tests require a dedicated PostgreSQL test database configured using `TEST_DATABASE_URL`. The test setup creates and deletes its own test database, so do not use a production database for this configuration.

### Run tests with coverage

```bash
uv run poe cov
```

The minimum required test coverage is 70%.

## Code quality

Run Ruff lint checks:

```bash
uv run poe lint
```

## Available commands

| Command | Description |
|---|---|
| `uv run poe dev` | Start development server |
| `uv run poe lint` | Run Ruff lint checks |
| `uv run poe test` | Run test suite |
| `uv run poe cov` | Run tests with coverage |
| `uv run poe migrate` | Apply database migrations |
| `uv run poe seed` | Load sample database records |
| `uv run poe test-integration` | Run integration tests |

## Day 4 checks

- Unit tests passing
- Ruff lint checks passing
- Test coverage above 70%
- Database integration tests created
- Docker configuration created
- Environment configuration documented

> **Note:** Integration tests require a configured test database. Docker commands require Docker Engine to be running.
