import asyncio

from sqlalchemy import text

from infra.db.session import engine


MIGRATION_SQL = [
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS question_type TEXT NOT NULL DEFAULT 'free_response'
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS choices JSON NOT NULL DEFAULT '[]'::json
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS correct_choice TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS validation_report JSON NOT NULL DEFAULT '{}'::json
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS generation_method TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS solver_code TEXT
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS distractor_metadata JSON NOT NULL DEFAULT '{}'::json
    """,
    """
    ALTER TABLE questions
    ADD COLUMN IF NOT EXISTS review_status TEXT
    """,
    """
    UPDATE questions
    SET question_type = 'free_response'
    WHERE question_type IS NULL
    """,
    """
    UPDATE questions
    SET choices = '[]'::json
    WHERE choices IS NULL
    """,
    """
    UPDATE questions
    SET validation_report = '{}'::json
    WHERE validation_report IS NULL
    """,
    """
    UPDATE questions
    SET distractor_metadata = '{}'::json
    WHERE distractor_metadata IS NULL
    """,
    """
    UPDATE questions
    SET review_status = 'draft'
    WHERE question_type = 'multiple_choice' AND review_status IS NULL
    """,
    """
    ALTER TABLE questions
    ALTER COLUMN question_type SET DEFAULT 'free_response'
    """,
    """
    ALTER TABLE questions
    ALTER COLUMN choices SET DEFAULT '[]'::json
    """,
    """
    ALTER TABLE questions
    ALTER COLUMN validation_report SET DEFAULT '{}'::json
    """,
    """
    ALTER TABLE questions
    ALTER COLUMN distractor_metadata SET DEFAULT '{}'::json
    """,
    """
    ALTER TABLE questions
    ALTER COLUMN question_type SET NOT NULL
    """,
    """
    ALTER TABLE questions
    ALTER COLUMN choices SET NOT NULL
    """,
    """
    ALTER TABLE questions
    ALTER COLUMN validation_report SET NOT NULL
    """,
    """
    ALTER TABLE questions
    ALTER COLUMN distractor_metadata SET NOT NULL
    """,
]


async def main() -> None:
    async with engine.begin() as connection:
        for statement in MIGRATION_SQL:
            await connection.execute(text(statement))

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
