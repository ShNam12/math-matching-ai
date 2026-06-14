from typing import Protocol

from infra.db.models import Question
from modules.question_classification.prompt_builder import (
    build_question_classification_prompt,
)
from modules.question_classification.schemas import (
    ClassificationCandidate,
    QuestionClassificationRequest,
    QuestionClassificationResult,
)
from modules.question_classification.validator import (
    validate_classification,
)
from modules.taxonomy import (
    TaxonomyDefinition,
    TaxonomyIndex,
    load_validated_taxonomy,
)


class QuestionClassifier(Protocol):
    def classify(
        self,
        prompt: str,
    ) -> ClassificationCandidate:
        ...


def _extract_formula_texts(
    formulas: list[dict[str, str]],
) -> list[str]:
    formula_texts: list[str] = []

    for formula in formulas:
        normalized_latex = str(
            formula.get("normalized_latex") or ""
        ).strip()

        latex = str(
            formula.get("latex") or ""
        ).strip()

        formula_text = normalized_latex or latex

        if formula_text and formula_text not in formula_texts:
            formula_texts.append(formula_text)

    return formula_texts


class QuestionClassificationService:
    def __init__(
        self,
        *,
        classifier: QuestionClassifier,
        taxonomy: TaxonomyDefinition | None = None,
        taxonomy_index: TaxonomyIndex | None = None,
    ) -> None:
        if (taxonomy is None) != (taxonomy_index is None):
            raise ValueError(
                "taxonomy and taxonomy_index must be provided together"
            )

        if taxonomy is None or taxonomy_index is None:
            taxonomy, taxonomy_index = load_validated_taxonomy()

        self.classifier = classifier
        self.taxonomy = taxonomy
        self.taxonomy_index = taxonomy_index

    def classify_question(
        self,
        question: Question,
    ) -> QuestionClassificationResult:
        request = QuestionClassificationRequest(
            question_id=question.id,
            statement=question.statement,
            solution=question.solution,
            answer=question.answer,
            formulas=_extract_formula_texts(question.formulas),
        )

        prompt = build_question_classification_prompt(
            request=request,
            taxonomy=self.taxonomy,
        )

        candidate = self.classifier.classify(prompt)

        return validate_classification(
            candidate,
            self.taxonomy,
            self.taxonomy_index,
        )