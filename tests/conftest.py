import pytest
from fastapi.testclient import TestClient

from djangodesk.api.deps import check_db, get_repo
from djangodesk.api.main import create_app
from djangodesk.config import Settings

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


@pytest.fixture
def db_state():
    return {"up": True}


@pytest.fixture
def client(db_state):
    settings = Settings(
        app_env="ci",
        database_url="postgresql://localhost:5432/unused",
        _env_file=None,
    )

    app = create_app(settings)

    app.dependency_overrides[get_repo] = lambda: FakeRepo(SAMPLE)
    app.dependency_overrides[check_db] = lambda: db_state["up"]

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
