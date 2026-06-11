from datetime import UTC, datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.models import Question
from modules.question_segmenter.schemas import SegmentedQuestion


class QuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def replace_for_document(
        self,
        *,
        document_id: str,
        segmented_questions: list[SegmentedQuestion],
    ) -> list[Question]:
        await self.session.execute(
            delete(Question).where(Question.document_id == document_id)
        )

        questions = [
            Question(
                document_id=document_id,
                sequence_number=question.sequence_number,
                marker=question.marker,
                marker_number=question.marker_number,
                statement=question.statement,
                solution=question.solution,
                answer=question.answer,
                formulas=[
                    formula.model_dump()
                    for formula in question.formulas
                ],
                subject=None,
                chapter=None,
                difficulty=None,
                skills=[],
                embedding_status="pending",
                embedding_model=None,
                embedding_dimension=None,
                embedding_error=None,
                embedded_at=None,
            )
            for question in segmented_questions
        ]

        self.session.add_all(questions)
        await self.session.commit()

        for question in questions:
            await self.session.refresh(question)

        return questions

    async def list_by_document(self, document_id: str) -> list[Question]:
        result = await self.session.execute(
            select(Question)
            .where(Question.document_id == document_id)
            .order_by(Question.sequence_number)
        )

        return list(result.scalars().all())

    async def get_question(self, question_id: str) -> Question | None:
        result = await self.session.execute(
            select(Question).where(Question.id == question_id)
        )

        return result.scalar_one_or_none()
    
    async def update_metadata(
        self,
        question: Question,
        *,
        subject: str | None = None,
        chapter: str | None = None,
        difficulty: str | None = None,
        skills: list[str] | None = None,
    ) -> Question:
        question.subject = subject
        question.chapter = chapter
        question.difficulty = difficulty

        if skills is not None:
            question.skills = skills

        await self.session.commit()
        await self.session.refresh(question)

        return question

    async def create_generated_question(
        self,
        *,
        source_question: Question,
        statement: str,
        solution: str | None,
        answer: str | None,
        formulas: list[dict[str, str]],
        subject: str | None,
        chapter: str | None,
        difficulty: str | None,
        skills: list[str],
    ) -> Question:
        result = await self.session.execute(
            select(func.max(Question.sequence_number)).where(
                Question.document_id == source_question.document_id
            )
        )
        max_sequence_number = result.scalar_one() or 0
        sequence_number = int(max_sequence_number) + 1

        question = Question(
            document_id=source_question.document_id,
            sequence_number=sequence_number,
            marker="Generated",
            marker_number=str(sequence_number),
            statement=statement,
            solution=solution,
            answer=answer,
            formulas=formulas,
            subject=subject,
            chapter=chapter,
            difficulty=difficulty,
            skills=skills,
            embedding_status="pending",
            embedding_model=None,
            embedding_dimension=None,
            embedding_error=None,
            embedded_at=None,
        )

        self.session.add(question)
        await self.session.commit()
        await self.session.refresh(question)

        return question
    
    async def list_by_ids(self, question_ids: list[str]) -> list[Question]:
        if not question_ids:
            return []

        result = await self.session.execute(
            select(Question).where(Question.id.in_(question_ids))
        )

        questions = list(result.scalars().all())
        questions_by_id = {
            question.id: question
            for question in questions
        }

        return [
            questions_by_id[question_id]
            for question_id in question_ids
            if question_id in questions_by_id
        ]
    
    async def mark_embedding_pending_for_document(
        self,
        document_id: str,
    ) -> None:
        await self.session.execute(
            update(Question)
            .where(Question.document_id == document_id)
            .values(
                embedding_status="pending",
                embedding_error=None,
                embedded_at=None,
            )
        )
        await self.session.commit()

    async def mark_embedding_completed_for_document(
        self,
        *,
        document_id: str,
        embedding_model: str,
        embedding_dimension: int,
    ) -> None:
        await self.session.execute(
            update(Question)
            .where(Question.document_id == document_id)
            .values(
                embedding_status="completed",
                embedding_model=embedding_model,
                embedding_dimension=embedding_dimension,
                embedding_error=None,
                embedded_at=datetime.now(UTC),
            )
        )
        await self.session.commit()

    async def mark_embedding_failed_for_document(
        self,
        *,
        document_id: str,
        error_message: str,
    ) -> None:
        await self.session.execute(
            update(Question)
            .where(Question.document_id == document_id)
            .values(
                embedding_status="failed",
                embedding_error=error_message[:4000],
            )
        )
        await self.session.commit()

    async def count_by_embedding_status(
        self,
        document_id: str,
    ) -> dict[str, int]:
        questions = await self.list_by_document(document_id)
        counts: dict[str, int] = {}

        for question in questions:
            counts[question.embedding_status] = (
                counts.get(question.embedding_status, 0) + 1
            )

        return counts