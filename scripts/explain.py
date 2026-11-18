"""Show how Postgres uses the GIN index for metadata queries."""

import asyncio
import json
import sys

from sqlalchemy import text

from djangodesk.config import get_settings
from djangodesk.db.session import make_engine

SQL = """
EXPLAIN ANALYZE
SELECT id, title
FROM documents
WHERE metadata @> CAST(:f AS jsonb)
"""


async def main(field: str, value: str) -> None:
    engine = make_engine(get_settings())
    params = {"f": json.dumps({field: value})}

    async with engine.connect() as conn:
        print("-- 1) Normal query plan:")
        result = await conn.execute(text(SQL), params)
        for line in result.scalars():
            print(line)

        await conn.execute(text("SET enable_seqscan = off"))

        print("\n-- 2) Query plan with sequential scans disabled:")
        result = await conn.execute(text(SQL), params)
        for line in result.scalars():
            print(line)

    await engine.dispose()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: uv run python scripts/explain.py <field> <value>")

    asyncio.run(main(sys.argv[1], sys.argv[2]))
