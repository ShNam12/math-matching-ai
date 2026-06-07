from modules.question_generation import (
    GeneratedQuestionCandidate,
    GeminiQuestionGenerator,
    GenerationConstraints,
    QuestionGenerationPreview,
    QuestionGenerationService,
)


def test_question_generation_exports_public_classes() -> None:
    assert GeneratedQuestionCandidate is not None
    assert GeminiQuestionGenerator is not None
    assert GenerationConstraints is not None
    assert QuestionGenerationPreview is not None
    assert QuestionGenerationService is not None