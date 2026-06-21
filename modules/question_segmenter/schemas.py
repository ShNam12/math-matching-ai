from typing import Any, Literal

from pydantic import BaseModel, Field


FormulaSource = Literal["statement", "solution", "answer", "choice"]


class ExtractedFormula(BaseModel):
    latex: str
    normalized_latex: str
    source: FormulaSource


class SegmentedChoice(BaseModel):
    key: str
    text: str
    latex: str | None = None
    is_correct: bool = False
    distractor_type: str | None = None
    rationale: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SegmentedQuestion(BaseModel):
    sequence_number: int
    marker: str
    marker_number: str
    statement: str
    solution: str | None = None
    answer: str | None = None
    formulas: list[ExtractedFormula]
    question_type: Literal["free_response", "multiple_choice"] = "free_response"
    choices: list[SegmentedChoice] = Field(default_factory=list)
    correct_choice: str | None = None


class SegmentationResult(BaseModel):
    preamble: str | None = None
    questions: list[SegmentedQuestion]
