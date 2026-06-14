from modules.question_classification.schemas import (
    ClassificationCandidate,
    ClassificationIssue,
    QuestionClassificationResult,
)
from modules.taxonomy import TaxonomyDefinition, TaxonomyIndex


class ClassificationValidationError(ValueError):
    def __init__(self, issues: list[ClassificationIssue]) -> None:
        self.issues = issues
        super().__init__("; ".join(issue.message for issue in issues))


def validate_classification(
    candidate: ClassificationCandidate,
    taxonomy: TaxonomyDefinition,
    index: TaxonomyIndex,
) -> QuestionClassificationResult:
    issues: list[ClassificationIssue] = []

    chapter = index.chapters.get(candidate.chapter_code)
    topic = index.topics.get(candidate.topic_code)
    problem_type = index.problem_types.get(candidate.problem_type_code)

    if chapter is None:
        issues.append(ClassificationIssue(
            code="unknown_chapter",
            field="chapter_code",
            message=f"Unknown chapter: {candidate.chapter_code}",
        ))

    if topic is None:
        issues.append(ClassificationIssue(
            code="unknown_topic",
            field="topic_code",
            message=f"Unknown topic: {candidate.topic_code}",
        ))
    elif chapter is not None and topic.parent != chapter.code:
        issues.append(ClassificationIssue(
            code="topic_parent_mismatch",
            field="topic_code",
            message="Topic does not belong to the selected chapter",
        ))

    if problem_type is None:
        issues.append(ClassificationIssue(
            code="unknown_problem_type",
            field="problem_type_code",
            message=f"Unknown problem type: {candidate.problem_type_code}",
        ))
    elif topic is not None and problem_type.parent != topic.code:
        issues.append(ClassificationIssue(
            code="problem_type_parent_mismatch",
            field="problem_type_code",
            message="Problem type does not belong to the selected topic",
        ))

    valid_skills = set(taxonomy.skill_vocabulary)
    for skill in candidate.skills:
        if skill not in valid_skills:
            issues.append(ClassificationIssue(
                code="unknown_skill",
                field="skills",
                message=f"Unknown skill: {skill}",
            ))

    if issues:
        raise ClassificationValidationError(issues)

    policy = taxonomy.confidence_policy
    if candidate.confidence >= policy.auto_accept:
        review_status = "auto_accept"
    elif candidate.confidence >= policy.soft_review_min:
        review_status = "soft_review"
    else:
        review_status = "mandatory_review"

    return QuestionClassificationResult(
        **candidate.model_dump(),
        subject_code=taxonomy.subject_code,
        subject_name=taxonomy.subject_display_name,
        chapter_name=chapter.display_name,
        topic_name=topic.display_name,
        problem_type_name=problem_type.display_name,
        taxonomy_id=taxonomy.taxonomy_id,
        taxonomy_version=taxonomy.version,
        review_status=review_status,
    )