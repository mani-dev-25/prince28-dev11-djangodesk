# DjangoDesk

A Django expert focused on ORM performance and security, answering from the official docs with code that runs and shows the SQL it produces.

**Status:** Day 1 foundation (FastAPI skeleton, quality gates). Live URL from Day 5.

## Who it's for

Python web developer at a Coimbatore startup whose Django admin pages became slow as data grew.

## The problem

Django's ORM hides SQL, so N+1 queries and missing indexes go unnoticed. Docs are large and version-specific.

## Data sources

Django documentation (docs/ folder in the repo) for the last 3 LTS versions, release notes, security release notes.

- https://github.com/django/django
- https://docs.djangoproject.com/
- Terms: Django docs BSD-licensed with the code.

## Hardest problem (my interview story)

ORM to SQL: answers about N+1 queries, select_related vs prefetch_related or annotate must give code that runs on a sample project and show the number of SQL queries before and after.

## Signature feature

ORM to SQL viewer: every ORM answer runs against a sample database and shows the SQL and query count.

## Target metric

90%+ of ORM code answers run and reduce queries as claimed on 30 tasks.

## Run it locally

```bash
uv sync
cp .env.example .env   # Windows: copy .env.example .env
uv run uvicorn djangodesk.api.main:create_app --factory --reload
```

Then open http://localhost:8000/docs

## Checks

```bash
uv run pytest
uv run ruff check .
```