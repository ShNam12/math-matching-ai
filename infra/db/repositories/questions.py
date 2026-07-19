from datetime import UTC, datetime

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.models import Question
from modules.question_segmenter.schemas import SegmentedQuestion

from modules.question_classification.schemas import (
    QuestionClassificationResult,
)


MCQ_REVIEW_STATUSES = {
    "draft",
    "generated",
    "validated",
    "needs_review",
    "approved",
    "rejected",
}


def infer_mcq_review_status(
    *,
    question_type: str | None,
    validation_report: dict[str, object] | None,
) -> str | None:
    if question_type != "multiple_choice":
        return None

    if not validation_report:
        return "generated"

    blocking_issues = validation_report.get("blocking_issues")
    warnings = validation_report.get("warnings")

    if isinstance(blocking_issues, list) and blocking_issues:
        return "needs_review"

    if isinstance(warnings, list) and warnings:
        return "needs_review"

    if validation_report.get("can_save") is False:
        return "needs_review"

    return "validated"


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
                question_type=question.question_type,
                choices=[
                    choice.model_dump()
                    for choice in question.choices
                ],
                correct_choice=question.correct_choice,
                validation_report={},
                generation_method=None,
                solver_code=None,
                distractor_metadata={},
                review_status=(
                    "draft"
                    if question.question_type == "multiple_choice"
                    else None
                ),
                formulas=[
                    formula.model_dump()
                    for formula in question.formulas
                ],
                subject=None,
                chapter=None,
                difficulty=None,
                skills=[],

                classification_status="pending",
                classification_model=None,
                classification_error=None,
                classified_at=None,
                
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
        question_type: str = "free_response",
        choices: list[dict[str, object]] | None = None,
        correct_choice: str | None = None,
        validation_report: dict[str, object] | None = None,
        generation_method: str | None = None,
        solver_code: str | None = None,
        distractor_metadata: dict[str, object] | None = None,
        review_status: str | None = None,
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
            question_type=question_type,
            choices=choices or [],
            correct_choice=correct_choice,
            validation_report=validation_report or {},
            generation_method=generation_method,
            solver_code=solver_code,
            distractor_metadata=distractor_metadata or {},
            review_status=review_status
            or infer_mcq_review_status(
                question_type=question_type,
                validation_report=validation_report,
            ),
            formulas=formulas,
            subject=subject,
            chapter=chapter,
            difficulty=difficulty,
            skills=skills,

            classification_status="pending",
            classification_model=None,
            classification_error=None,
            classified_at=None,

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

    async def update_review_status(
        self,
        question: Question,
        *,
        review_status: str,
    ) -> Question:
        normalized_status = review_status.strip().lower()

        if normalized_status not in MCQ_REVIEW_STATUSES:
            allowed = ", ".join(sorted(MCQ_REVIEW_STATUSES))
            raise ValueError(f"Invalid review_status. Allowed: {allowed}")

        question.review_status = normalized_status

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

    async def mark_embedding_pending_for_question(
        self,
        question_id: str,
    ) -> None:
        await self.session.execute(
            update(Question)
            .where(Question.id == question_id)
            .values(
                embedding_status="pending",
                embedding_error=None,
                embedded_at=None,
            )
        )
        await self.session.commit()

    async def mark_embedding_completed_for_question(
        self,
        *,
        question_id: str,
        embedding_model: str,
        embedding_dimension: int,
    ) -> None:
        await self.session.execute(
            update(Question)
            .where(Question.id == question_id)
            .values(
                embedding_status="completed",
                embedding_model=embedding_model,
                embedding_dimension=embedding_dimension,
                embedding_error=None,
                embedded_at=datetime.now(UTC),
            )
        )
        await self.session.commit()

    async def mark_embedding_failed_for_question(
        self,
        *,
        question_id: str,
        error_message: str,
    ) -> None:
        await self.session.execute(
            update(Question)
            .where(Question.id == question_id)
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
    
    async def update_classification(
        self,
        question: Question,
        *,
        result: QuestionClassificationResult,
        classification_model: str,
    ) -> Question:
        question.subject = result.subject_name
        question.subject_code = result.subject_code

        # Giữ field chapter cũ để tương thích API hiện tại.
        question.chapter = result.chapter_name
        question.chapter_code = result.chapter_code
        question.chapter_name = result.chapter_name

        question.topic_code = result.topic_code
        question.topic_name = result.topic_name
        question.problem_type_code = result.problem_type_code
        question.problem_type_name = result.problem_type_name

        question.difficulty = result.difficulty
        question.skills = result.skills

        question.taxonomy_id = result.taxonomy_id
        question.taxonomy_version = result.taxonomy_version
        question.taxonomy_confidence = result.confidence
        question.taxonomy_reason = result.reason
        question.review_status = result.review_status

        question.classification_status = "completed"
        question.classification_model = classification_model
        question.classification_error = None
        question.classified_at = datetime.now(UTC)

        await self.session.commit()
        await self.session.refresh(question)

        return question

    async def mark_classification_failed(
        self,
        question: Question,
        *,
        error_message: str,
        classification_model: str,
    ) -> Question:
        question.classification_status = "failed"
        question.classification_model = classification_model
        question.classification_error = error_message[:4000]

        await self.session.commit()
        await self.session.refresh(question)

        return question

    async def mark_classification_pending_for_document(
        self,
        document_id: str,
    ) -> None:
        await self.session.execute(
            update(Question)
            .where(Question.document_id == document_id)
            .values(
                classification_status="pending",
                classification_error=None,
                classified_at=None,
            )
        )
        await self.session.commit()

    async def list_unclassified_by_document(
        self,
        document_id: str,
    ) -> list[Question]:
        result = await self.session.execute(
            select(Question)
            .where(
                Question.document_id == document_id,
                Question.classification_status != "completed",
            )
            .order_by(Question.sequence_number)
        )

        return list(result.scalars().all())

    async def count_by_taxonomy(
        self,
        *,
        document_id: str | None = None,
    ) -> list[dict[str, str | int | None]]:
        statement = (
            select(
                Question.chapter_code,
                Question.topic_code,
                Question.problem_type_code,
                func.count(Question.id).label("question_count"),
            )
            .where(Question.classification_status == "completed")
            .group_by(
                Question.chapter_code,
                Question.topic_code,
                Question.problem_type_code,
            )
            .order_by(
                Question.chapter_code,
                Question.topic_code,
                Question.problem_type_code,
            )
        )

        if document_id is not None:
            statement = statement.where(
                Question.document_id == document_id
            )

        result = await self.session.execute(statement)

        return [
            {
                "chapter_code": chapter_code,
                "topic_code": topic_code,
                "problem_type_code": problem_type_code,
                "question_count": int(question_count),
            }
            for (
                chapter_code,
                topic_code,
                problem_type_code,
                question_count,
            ) in result.all()
        ]
    
    async def list_by_taxonomy(
        self,
        *,
        chapter_code: str | None = None,
        topic_code: str | None = None,
        problem_type_code: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Question]:
        statement = (
            select(Question)
            .where(Question.classification_status == "completed")
            .order_by(Question.updated_at.desc(), Question.sequence_number)
            .limit(limit)
            .offset(offset)
        )

        if chapter_code is not None:
            statement = statement.where(
                Question.chapter_code == chapter_code
            )

        if topic_code is not None:
            statement = statement.where(
                Question.topic_code == topic_code
            )

        if problem_type_code is not None:
            statement = statement.where(
                Question.problem_type_code == problem_type_code
            )

        result = await self.session.execute(statement)

        return list(result.scalars().all())
