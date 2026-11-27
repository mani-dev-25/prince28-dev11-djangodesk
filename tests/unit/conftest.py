import pytest
from fastapi.testclient import TestClient

from djangodesk.api.deps import (
    check_db,
    get_gateway,
    get_ingest_repo,
    get_manifest,
    get_queue,
    get_repo,
    get_usage_repo,
)
from djangodesk.api.main import create_app
from djangodesk.config import Settings
from djangodesk.llm.gateway import FakeLLM, LLMGateway

SAMPLE = [
    {
        "id": "001",
        "title": "Alpha guideline",
        "year": 2023,
        "category": "guide",
    },
    {
        "id": "002",
        "title": "Beta circular",
        "year": 2024,
        "category": "circular",
    },
    {
        "id": "003",
        "title": "Gamma notice",
        "year": 2025,
        "category": "notice",
    },
]


class FakeRepo:
    def __init__(self, records):
        self.records = records

    async def list(self, *, q, filters, limit, offset):
        records = self.records

        if q:
            records = [record for record in records if q.lower() in str(record).lower()]

        for key, value in filters.items():
            records = [
                record for record in records if str(record.get(key, "")).lower() == value.lower()
            ]

        total = len(records)
        return total, records[offset : offset + limit]

    async def get(self, external_id):
        return next(
            (record for record in self.records if record["id"] == external_id),
            None,
        )


class FakeUsage:
    async def by_day(self, days=7):
        return [
            {
                "day": "2026-11-25",
                "calls": 3,
                "errors": 1,
                "fallbacks": 1,
                "tokens_in": 300,
                "tokens_out": 120,
                "cost_inr": 0.0642,
            }
        ]


@pytest.fixture
def db_state():
    return {"up": True}


@pytest.fixture
def llm():
    return FakeLLM()


@pytest.fixture
def client(db_state, llm, queue, ingest_repo):
    settings = Settings(
        app_env="ci",
        database_url="postgresql://localhost:5432/unused",
        admin_token="test-token",
        _env_file=None,
    )

    app = create_app(settings)

    app.dependency_overrides[get_repo] = lambda: FakeRepo(SAMPLE)
    app.dependency_overrides[check_db] = lambda: db_state["up"]
    app.dependency_overrides[get_gateway] = lambda: LLMGateway([llm])
    app.dependency_overrides[get_usage_repo] = lambda: FakeUsage()
    app.dependency_overrides[get_queue] = lambda: queue
    app.dependency_overrides[get_ingest_repo] = lambda: ingest_repo
    app.dependency_overrides[get_manifest] = lambda: MANIFEST

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


MANIFEST = [
    {
        "url": f"https://x.test/{number}.pdf",
        "source": "x",
        "licence": "CC BY 4.0",
        "path": f"data/raw/x/{number}.pdf",
        "sha256": str(number) * 64,
        "status": "downloaded",
    }
    for number in (1, 2)
]
