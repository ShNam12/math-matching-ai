from pydantic import BaseModel, Field


class AnalyticsSummaryResponse(BaseModel):
    document_count: int
    completed_document_count: int
    failed_document_count: int
    question_count: int
    embedded_question_count: int
    formula_count: int
    multiple_choice_question_count: int = 0
    free_response_question_count: int = 0
    validated_mcq_count: int = 0
    blocking_mcq_count: int = 0
    symbolic_validated_question_count: int = 0
    correct_answer_error_count: int = 0
    distractor_error_count: int = 0
    solver_unavailable_count: int = 0
    needs_review_count: int = 0
    valid_mcq_rate: float = 0.0
    correct_answer_error_rate: float = 0.0
    distractor_error_rate: float = 0.0
    solver_unavailable_rate: float = 0.0
    needs_review_rate: float = 0.0
    embedding_status_counts: dict[str, int]
    question_type_counts: dict[str, int] = Field(default_factory=dict)
    difficulty_counts: dict[str, int]
    chapter_counts: dict[str, int]
    topic_counts: dict[str, int] = Field(default_factory=dict)
    generation_method_counts: dict[str, int] = Field(default_factory=dict)
