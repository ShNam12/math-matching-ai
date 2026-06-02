from sqlalchemy import delete, select
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