from pydantic import BaseModel


class AnalyticsSummaryResponse(BaseModel):
    document_count: int
    completed_document_count: int
    failed_document_count: int
    question_count: int
    embedded_question_count: int
    formula_count: int
    embedding_status_counts: dict[str, int]
    difficulty_counts: dict[str, int]
    chapter_counts: dict[str, int]