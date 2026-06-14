from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from modules.taxonomy.schemas import Difficulty


ReviewStatus = Literal[
    "auto_accept",
    "soft_review",
    "mandatory_review",
]


class ClassificationModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class QuestionClassificationRequest(ClassificationModel):
    question_id: str = Field(min_length=1)
    statement: str = Field(min_length=1)
    solution: str | None = None
    answer: str | None = None
    formulas: list[str] = Field(default_factory=list)

    @field_validator("statement")
    @classmethod
    def validate_statement(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("statement must not be blank")
        return value


class ClassificationCandidate(ClassificationModel):
    chapter_code: str = Field(min_length=1)
    topic_code: str = Field(min_length=1)
    problem_type_code: str = Field(min_length=1)

    skills: list[str] = Field(min_length=1)
    difficulty: Difficulty
    confidence: float = Field(ge=0, le=1)
    reason: str = Field(min_length=1)

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("reason must not be blank")
        return value


class QuestionClassificationResult(ClassificationCandidate):
    subject_code: str
    subject_name: str

    chapter_name: str
    topic_name: str
    problem_type_name: str

    taxonomy_id: str
    taxonomy_version: str
    review_status: ReviewStatus


class ClassificationIssue(ClassificationModel):
    code: str
    message: str
    field: str | None = None