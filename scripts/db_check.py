"""Check PostgreSQL connection and document count."""

import asyncio

from sqlalchemy import text

from djangodesk.db.session import engine


async def main() -> None:
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT COUNT(*) FROM documents"))
            count = result.scalar_one()

            print("Database connection successful!")
            print(f"Total documents: {count}")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
