import asyncio

from sqlalchemy import text

from infra.db.session import engine


MIGRATION_SQL = [
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS embedding_status TEXT NOT NULL DEFAULT 'pending'
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS embedding_model TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS embedding_dimension INTEGER
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS embedding_error TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS embedded_at TIMESTAMPTZ
    """,
]


async def main() -> None:
    async with engine.begin() as conn:
        for statement in MIGRATION_SQL:
            await conn.execute(text(statement))

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())