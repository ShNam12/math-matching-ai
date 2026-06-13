from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Difficulty = Literal["easy", "medium", "hard"]
TaxonomyLevel = Literal["chapter", "topic", "problem_type"]


class TaxonomyModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ConfidencePolicy(TaxonomyModel):
    auto_accept: float = Field(ge=0, le=1)
    soft_review_min: float = Field(ge=0, le=1)
    mandatory_review_below: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def validate_threshold_order(self) -> "ConfidencePolicy":
        if self.mandatory_review_below != self.soft_review_min:
            raise ValueError(
                "mandatory_review_below must equal soft_review_min"
            )
        if self.soft_review_min >= self.auto_accept:
            raise ValueError(
                "soft_review_min must be lower than auto_accept"
            )
        return self


class TaxonomyExpectedCounts(TaxonomyModel):
    chapters: int = Field(gt=0)
    topics: int = Field(gt=0)
    problem_types: int = Field(gt=0)


class KnowledgeNode(TaxonomyModel):
    code: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    level: TaxonomyLevel
    parent: str | None
    description: str = Field(min_length=1)
    aliases: list[str] = Field(default_factory=list)
    positive_signals: list[str] = Field(default_factory=list)
    negative_signals: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    default_difficulty: Difficulty | None = None
    confusable_with: list[str] = Field(default_factory=list)
    examples: list[dict[str, Any]] = Field(default_factory=list)


class ProblemTypeNode(KnowledgeNode):
    level: Literal["problem_type"]
    parent: str = Field(min_length=1)
    default_difficulty: Difficulty


class TopicNode(KnowledgeNode):
    level: Literal["topic"]
    parent: str = Field(min_length=1)
    problem_types: list[ProblemTypeNode] = Field(min_length=1)


class ChapterNode(KnowledgeNode):
    level: Literal["chapter"]
    parent: None = None
    topics: list[TopicNode] = Field(min_length=1)


class TaxonomyDefinition(TaxonomyModel):
    taxonomy_id: str = Field(min_length=1)
    version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    subject_code: str = Field(min_length=1)
    subject_display_name: str = Field(min_length=1)
    institution: str = Field(min_length=1)
    program: str = Field(min_length=1)
    language: str = Field(min_length=2)
    levels: list[TaxonomyLevel] = Field(min_length=3, max_length=3)
    difficulty_levels: list[Difficulty] = Field(min_length=3, max_length=3)
    confidence_policy: ConfidencePolicy
    source_documents: list[str] = Field(min_length=1)
    skill_vocabulary: list[str] = Field(min_length=1)
    expected_counts: TaxonomyExpectedCounts
    chapters: list[ChapterNode] = Field(min_length=1)
