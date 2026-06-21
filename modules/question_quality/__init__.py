from modules.question_quality.schemas import (
    QualityIssue,
    QuestionQualityReport,
    QuestionValidationReport,
    SemanticDuplicateHit,
    SymbolicCheckResult,
    TaxonomyQualityReport,
)
__all__ = [
    "QualityIssue",
    "QuestionQualityReport",
    "QuestionQualityService",
    "QuestionValidationReport",
    "SemanticDuplicateHit",
    "SymbolicCheckResult",
    "TaxonomyClassificationQualityService",
    "TaxonomyQualityReport",
]


def __getattr__(name: str):
    if name in {
        "QuestionQualityService",
        "TaxonomyClassificationQualityService",
    }:
        from modules.question_quality.service import (
            QuestionQualityService,
            TaxonomyClassificationQualityService,
        )

        values = {
            "QuestionQualityService": QuestionQualityService,
            "TaxonomyClassificationQualityService": (
                TaxonomyClassificationQualityService
            ),
        }
        return values[name]

    raise AttributeError(name)
