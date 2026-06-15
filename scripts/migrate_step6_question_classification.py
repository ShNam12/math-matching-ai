import asyncio

from sqlalchemy import text

from infra.db.session import engine


MIGRATION_SQL = [
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS subject_code TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS chapter_code TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS chapter_name TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS topic_code TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS topic_name TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS problem_type_code TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS problem_type_name TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS taxonomy_id TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS taxonomy_version TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS taxonomy_confidence DOUBLE PRECISION
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS taxonomy_reason TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS review_status TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS classification_status
    TEXT NOT NULL DEFAULT 'pending'
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS classification_model TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS classification_error TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS classified_at TIMESTAMPTZ
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_questions_chapter_code
    ON questions (chapter_code)
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_questions_topic_code
    ON questions (topic_code)
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_questions_problem_type_code
    ON questions (problem_type_code)
    """,
    """
    CREATE INDEX IF NOT EXISTS ix_questions_classification_status
    ON questions (classification_status)
    """,
]


async def main() -> None:
    async with engine.begin() as connection:
        for statement in MIGRATION_SQL:
            await connection.execute(text(statement))

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())