import os
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from djangodesk.db.models import Document, Page
from djangodesk.db.repository import DocumentRepository

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
async def db_engine(test_database):
    engine = create_async_engine(test_database)
    yield engine
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with factory() as session:
        yield session


@pytest.mark.asyncio
async def test_migrations_create_tables(db_engine):
    async with db_engine.connect() as connection:
        tables = await connection.run_sync(lambda conn: inspect(conn).get_table_names())

    assert "documents" in tables
    assert "pages" in tables
    assert "alembic_version" in tables


@pytest.mark.asyncio
async def test_document_external_id_is_unique(db_session):
    db_session.add_all(
        [
            Document(external_id="unique-test", title="First", sha256="a" * 64),
            Document(external_id="unique-test", title="Duplicate", sha256="b" * 64),
        ]
    )

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_page_number_must_be_positive(db_session):
    document = Document(
        external_id="page-test",
        title="Page test",
        sha256="c" * 64,
    )
    db_session.add(document)
    await db_session.flush()

    db_session.add(Page(document_id=document.id, page_no=0, text="Invalid page"))

    with pytest.raises(IntegrityError):
        await db_session.commit()


@pytest.mark.asyncio
async def test_deleting_document_deletes_pages(db_session):
    document = Document(
        external_id="cascade-test",
        title="Cascade test",
        sha256="d" * 64,
    )
    document.pages.append(Page(page_no=1, text="Page one"))
    db_session.add(document)
    await db_session.commit()

    document_id = document.id
    await db_session.delete(document)
    await db_session.commit()

    remaining = await db_session.scalar(select(Page).where(Page.document_id == document_id))

    assert remaining is None


@pytest.mark.asyncio
async def test_repository_searches_real_database(db_session):
    db_session.add(
        Document(
            external_id="search-test",
            title="Integration testing document",
            sha256="e" * 64,
            metadata_={"topic": "database testing"},
        )
    )
    await db_session.commit()

    repository = DocumentRepository(db_session)
    total, results = await repository.list(
        q="Integration testing",
        filters={},
        limit=10,
        offset=0,
    )

    assert total == 1
    assert results[0]["id"] == "search-test"


@pytest.mark.asyncio
async def test_loader_is_idempotent(test_database):
    env = os.environ.copy()
    env["DATABASE_URL"] = test_database
    env["APP_ENV"] = "ci"

    first_run = subprocess.run(
        ["uv", "run", "python", "scripts/load_db.py"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    second_run = subprocess.run(
        ["uv", "run", "python", "scripts/load_db.py"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )

    assert "inserted=" in first_run.stdout
    assert "unchanged=" in second_run.stdout
    assert "updated=0" in second_run.stdout
