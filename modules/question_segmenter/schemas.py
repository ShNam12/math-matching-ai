from typing import Literal

from pydantic import BaseModel


FormulaSource = Literal["statement", "solution", "answer"]


class ExtractedFormula(BaseModel):
    latex: str
    normalized_latex: str
    source: FormulaSource


class SegmentedQuestion(BaseModel):
    sequence_number: int
    marker: str
    marker_number: str
    statement: str
    solution: str | None = None
    answer: str | None = None
    formulas: list[ExtractedFormula]


class SegmentationResult(BaseModel):
    preamble: str | None = None
    questions: list[SegmentedQuestion]