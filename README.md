# DjangoDesk

<p align="center">
  <strong>An AI-assisted Django ORM performance and security learning assistant</strong>
</p>

<p align="center">
  Built with FastAPI, PostgreSQL, pgvector, Docker, and GitHub Actions.
</p>

<p align="center">
  <a href="https://github.com/mani-dev-25/prince28-dev11-djangodesk/actions/workflows/ci.yml">
    <img src="https://github.com/mani-dev-25/prince28-dev11-djangodesk/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://github.com/mani-dev-25/prince28-dev11-djangodesk/actions/workflows/cd.yml">
    <img src="https://github.com/mani-dev-25/prince28-dev11-djangodesk/actions/workflows/cd.yml/badge.svg" alt="CD">
  </a>
</p>

---

## Live Application

**Live:** https://djangodesk-iagt.onrender.com

**Health Check:** https://djangodesk-iagt.onrender.com/health

---

## Overview

DjangoDesk is an AI-assisted learning and development project focused on understanding Django ORM performance, query optimization, and security-related concepts.

The project provides a backend foundation for exploring ORM-related problems, understanding database behavior, and developing an AI-assisted tool that helps developers learn better Django ORM practices.

The project is built using modern Python backend technologies, PostgreSQL, Docker, automated testing, and CI/CD workflows.

---

## Problem Statement

Developers using Django ORM may face problems such as:

- N+1 query problems
- Unnecessary database queries
- Improper ORM usage
- Inefficient relationships and query patterns
- Performance bottlenecks
- Potential security mistakes

Understanding these problems can be difficult for beginners because ORM code often hides the SQL queries generated behind it.

DjangoDesk aims to make ORM learning and analysis easier through an AI-assisted development approach.

---

## Objectives

- Build a Python backend application using FastAPI.
- Work with PostgreSQL as the primary database.
- Explore database performance and query optimization.
- Use SQLAlchemy and Alembic for database operations and migrations.
- Build a structured foundation for AI-assisted ORM analysis.
- Implement automated testing and code-quality checks.
- Containerize the application using Docker.
- Implement CI/CD using GitHub Actions.
- Deploy the application to Render.

---

## Tech Stack

### Backend

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- Alembic
- Async programming

### Database

- PostgreSQL
- Neon PostgreSQL
- pgvector
- JSONB
- GIN Indexing

### Development Tools

- UV
- Ruff
- pytest
- pytest-cov
- pre-commit
- Git

### DevOps

- Docker
- Docker Compose
- GitHub Actions
- Render

---

## Architecture

```text
                 Developer
                    |
                    v
             GitHub Repository
                    |
                    v
            GitHub Actions CI
         -----------------------
         |                     |
      Testing                Linting
         |                     |
         -----------+-----------
                    |
                    v
               CD Workflow
                    |
            Alembic Migration
                    |
                    v
              Render Deploy
                    |
                    v
            DjangoDesk FastAPI
                    |
                    v
             Neon PostgreSQL
```

---

## Project Structure

```text
djangodesk/
│
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
│
├── data/
│   └── sample_records.json
│
├── docs/
│   ├── QUESTIONS.md
│   └── REQUIREMENTS.md
│
├── migrations/
│   ├── versions/
│   └── env.py
│
├── scripts/
│   ├── load_db.py
│   └── smoke.py
│
├── src/
│   └── djangodesk/
│       ├── api/
│       │   └── main.py
│       ├── db/
│       │   └── models.py
│       └── config.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── uv.lock
├── README.md
└── NOTES.md
```

---

## Run Locally

### Requirements

Make sure you have installed:

- Python 3.12
- UV
- Git
- Docker Desktop (for Docker-based setup)

### 1. Clone the repository

```bash
git clone https://github.com/mani-dev-25/prince28-dev11-djangodesk.git
```

```bash
cd prince28-dev11-djangodesk
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

Copy the example environment file:

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**Linux/macOS:**

```bash
cp .env.example .env
```

Update the `.env` file with your required configuration.

Never commit your `.env` file or expose database credentials.

### 4. Run database migrations

```bash
uv run alembic upgrade head
```

### 5. Start the application

```bash
uv run uvicorn djangodesk.api.main:app --reload
```

The local application should be accessible at:

```text
http://127.0.0.1:8000
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

---

## Run locally in one command

Start the application and required services using Docker Compose:

```bash
docker compose up --build
```

To stop the services:

```bash
docker compose down
```

To run unit tests locally:

```bash
uv run pytest tests/unit
```

---

## Docker

Build the Docker image:

```bash
docker build -t djangodesk .
```

Run the application container:

```bash
docker run --env-file .env -p 8000:8000 djangodesk
```

Alternatively, use Docker Compose:

```bash
docker compose up --build
```

Stop Docker Compose:

```bash
docker compose down
```

---

## Database

DjangoDesk uses PostgreSQL for structured data storage.

### Database Features Used

- PostgreSQL relational database
- SQLAlchemy ORM
- Alembic migrations
- JSONB fields
- GIN indexes
- pgvector extension support

### Database Migrations

Apply migrations:

```bash
uv run alembic upgrade head
```

Check the current migration:

```bash
uv run alembic current
```

View migration history:

```bash
uv run alembic history
```

Create a new migration:

```bash
uv run alembic revision --autogenerate -m "describe_change"
```

---

## Data Loading

Sample data is provided through:

```text
data/sample_records.json
```

Load the data into the database:

```bash
uv run python scripts/load_db.py
```

The data loader supports idempotent behavior, preventing duplicate records when the same data is loaded multiple times.

---

## Testing

DjangoDesk uses pytest for automated testing.

### Run unit tests

```bash
uv run pytest tests/unit
```

### Run all tests

```bash
uv run pytest
```

### Run tests with coverage

```bash
uv run pytest --cov=djangodesk
```

### Current Test Results

- Unit tests: 17 passed
- Unit test suite successfully verified during the Week 1 self-check.

---

## Code Quality

Ruff is used for linting.

Run Ruff:

```bash
uv run ruff check .
```

Run pre-commit checks:

```bash
uv run pre-commit run --all-files
```

Install pre-commit hooks:

```bash
uv run pre-commit install
```

---

## CI/CD Pipeline

DjangoDesk uses GitHub Actions to automate testing and deployment.

### Continuous Integration

The CI workflow is located at:

```text
.github/workflows/ci.yml
```

The CI pipeline performs automated checks, including:

- Dependency installation
- Code quality checks
- Automated tests
- Docker build validation

CI workflow:

https://github.com/mani-dev-25/prince28-dev11-djangodesk/actions/workflows/ci.yml

### Continuous Deployment

The CD workflow is located at:

```text
.github/workflows/cd.yml
```

The CD workflow automates:

1. Installing Python and UV.
2. Installing project dependencies.
3. Running Alembic database migrations.
4. Triggering Render deployment through a deploy hook.
5. Waiting for the deployment.
6. Checking the live health endpoint.
7. Failing the workflow if the health check does not succeed.

CD workflow:

https://github.com/mani-dev-25/prince28-dev11-djangodesk/actions/workflows/cd.yml

---

## Deployment

DjangoDesk is deployed using Render.

### Deployment Components

| Component | Platform |
|---|---|
| Application hosting | Render |
| Database | Neon PostgreSQL |
| CI | GitHub Actions |
| CD | GitHub Actions |
| Containerization | Docker |

### Live Deployment

```text
https://djangodesk-iagt.onrender.com
```

### Health Check

```text
https://djangodesk-iagt.onrender.com/health
```

Expected response:

```json
{
  "status": "ok",
  "app": "djangodesk",
  "env": "production",
  "version": "dev"
}
```

The exact response values may differ based on the deployed environment and application version.

---

## Smoke Testing

A smoke-test script is available to verify the live application.

```bash
uv run python scripts/smoke.py https://djangodesk-iagt.onrender.com
```

Successful result:

```text
Checking: https://djangodesk-iagt.onrender.com/health
SMOKE TEST PASSED
HTTP Status: 200
Application: djangodesk
Version: dev
```

This confirms that the deployed application is responding successfully to health-check requests.

---

## Engineering Notes

Engineering observations, migration checks, database experiments, idempotency tests, query plans, deployment notes, and rollback procedures are documented in:

```text
NOTES.md
```

Topics include:

- Database migrations
- Data-loader idempotency
- PostgreSQL query plans
- GIN index behavior
- CI/CD
- Deployment verification
- Rollback procedures

---

## Week 1 Progress

| Day | Focus | Status |
|---|---|---|
| Day 1 | Repository setup, requirements, FastAPI foundation | Completed |
| Day 2 | Sample data and data-loading tasks | Completed |
| Day 3 | PostgreSQL, migrations, indexing | Completed |
| Day 4 | Docker, Compose and automated testing | Completed |
| Day 5 | CI/CD, live deployment and rollback drill | In Progress |

---

## Week 1 Self-Check

Run the self-check script:

```bash
uv run python scripts/check_week1.py
```

To include the live deployment check:

```bash
uv run python scripts/check_week1.py https://djangodesk-iagt.onrender.com
```

The script checks project files, repository configuration, tests, Docker, CI/CD configuration, deployment information, and the live health endpoint.

---

## Roadmap

- [x] Project repository setup
- [x] FastAPI application foundation
- [x] PostgreSQL integration
- [x] Alembic migrations
- [x] Data loader
- [x] Docker setup
- [x] Unit tests
- [x] CI pipeline
- [x] CD pipeline
- [x] Render deployment
- [x] Health check
- [x] Smoke test
- [ ] Perform rollback drill on Render
- [ ] Verify roll-forward after rollback
- [ ] Document rollback and roll-forward SHAs and timestamps
- [x] Add CI/CD badges to README
- [ ] Complete Week 1 final self-check
- [ ] Continue AI-assisted ORM analysis development
- [ ] Build deeper ORM performance analysis features
- [ ] Improve AI-based explanations and learning workflow

---

## Learning Outcomes

Through this project, the following concepts are practiced:

- Backend application development using FastAPI
- Python project management using UV
- PostgreSQL database management
- SQLAlchemy ORM
- Database migrations using Alembic
- JSONB storage and GIN indexing
- Docker and Docker Compose
- Automated unit testing with pytest
- Code-quality checking with Ruff
- CI/CD using GitHub Actions
- Cloud deployment using Render
- Deployment health checks
- Database and deployment troubleshooting

---

## Author

**Manikandan A**

GitHub: [mani-dev-25](https://github.com/mani-dev-25)

Project Repository:

[prince28-dev11-djangodesk](https://github.com/mani-dev-25/prince28-dev11-djangodesk)

---

## License

This project is developed as part of a learning and development project. Please check the repository for licensing information.
