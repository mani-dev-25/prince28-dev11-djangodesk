"""Check whether the application can connect to PostgreSQL."""

import asyncio

from sqlalchemy import text

from djangodesk.db.session import engine


async def main() -> None:
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT 1"))
            print(f"Database connection successful: {result.scalar_one()}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
