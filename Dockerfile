FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY . .

RUN uv sync --frozen

FROM python:3.12-slim AS runtime

ARG GIT_SHA=dev
ENV GIT_SHA=${GIT_SHA}

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app app && id app

COPY --chown=app:app data ./data
COPY --chown=app:app prompts ./prompts

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

USER app

EXPOSE 8000

CMD ["uvicorn", "djangodesk.api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
