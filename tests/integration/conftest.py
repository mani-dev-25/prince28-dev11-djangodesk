import os
import subprocess
from pathlib import Path

import asyncpg
import pytest
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[2]
TEST_DB_NAME = "djangodesk_test"


@pytest.fixture(scope="session")
def test_database():
    admin_url = os.getenv("TEST_DATABASE_URL")

    if not admin_url:
        pytest.skip("TEST_DATABASE_URL is not configured")

    url = make_url(admin_url)

    connection_url = url.set(
        drivername="postgresql",
        database="postgres",
    ).render_as_string(hide_password=False)

    test_url = url.set(database=TEST_DB_NAME)

    async def create_database():
        connection = await asyncpg.connect(connection_url)
        try:
            await connection.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"')
            await connection.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
        finally:
            await connection.close()

    async def drop_database():
        connection = await asyncpg.connect(connection_url)
        try:
            await connection.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}"')
        finally:
            await connection.close()

    import asyncio

    asyncio.run(create_database())

    env = os.environ.copy()
    env["DATABASE_URL"] = test_url.render_as_string(hide_password=False)
    env["APP_ENV"] = "ci"

    try:
        subprocess.run(
            ["uv", "run", "alembic", "upgrade", "head"],
            cwd=ROOT,
            env=env,
            check=True,
        )
        yield env["DATABASE_URL"]
    finally:
        asyncio.run(drop_database())
