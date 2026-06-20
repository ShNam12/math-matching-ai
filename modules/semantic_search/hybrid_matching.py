from dataclasses import dataclass


@dataclass(frozen=True)
class HybridScoreBreakdown:
    semantic_score: float
    taxonomy_score: float
    formula_score: float
    difficulty_score: float
    skill_score: float
    final_score: float


@dataclass(frozen=True)
class HybridMatchingContext:
    chapter_code: str | None = None
    topic_code: str | None = None
    problem_type_code: str | None = None
    difficulty: str | None = None
    skills: list[str] | None = None


@dataclass(frozen=True)
class HybridMatchingCandidate:
    semantic_score: float
    chapter_code: str | None = None
    topic_code: str | None = None
    problem_type_code: str | None = None
    difficulty: str | None = None
    skills: list[str] | None = None
    formula_score: float = 0.0


def clamp_score(value: float) -> float:
    return max(0.0, min(1.0, value))

def has_hybrid_context(context: HybridMatchingContext) -> bool:
    return any([
        context.chapter_code,
        context.topic_code,
        context.problem_type_code,
        context.difficulty,
        context.skills,
    ])

def calculate_taxonomy_score(
    *,
    context: HybridMatchingContext,
    candidate: HybridMatchingCandidate,
) -> float:
    if (
        context.problem_type_code
        and candidate.problem_type_code
        and context.problem_type_code == candidate.problem_type_code
    ):
        return 1.0

    if (
        context.topic_code
        and candidate.topic_code
        and context.topic_code == candidate.topic_code
    ):
        return 0.7

    if (
        context.chapter_code
        and candidate.chapter_code
        and context.chapter_code == candidate.chapter_code
    ):
        return 0.4

    return 0.0


def calculate_difficulty_score(
    *,
    context: HybridMatchingContext,
    candidate: HybridMatchingCandidate,
) -> float:
    if not context.difficulty or not candidate.difficulty:
        return 0.0

    if context.difficulty == candidate.difficulty:
        return 1.0

    compatible = {
        ("easy", "medium"),
        ("medium", "easy"),
        ("medium", "hard"),
        ("hard", "medium"),
    }

    if (context.difficulty, candidate.difficulty) in compatible:
        return 0.5

    return 0.0


def calculate_skill_score(
    *,
    context: HybridMatchingContext,
    candidate: HybridMatchingCandidate,
) -> float:
    context_skills = set(context.skills or [])
    candidate_skills = set(candidate.skills or [])

    if not context_skills or not candidate_skills:
        return 0.0

    overlap = context_skills & candidate_skills
    union = context_skills | candidate_skills

    return len(overlap) / len(union)


def calculate_hybrid_score(
    *,
    context: HybridMatchingContext,
    candidate: HybridMatchingCandidate,
) -> HybridScoreBreakdown:
    semantic_score = clamp_score(candidate.semantic_score)
    formula_score = clamp_score(candidate.formula_score)

    if not has_hybrid_context(context):
        return HybridScoreBreakdown(
            semantic_score=semantic_score,
            taxonomy_score=0.0,
            formula_score=formula_score,
            difficulty_score=0.0,
            skill_score=0.0,
            final_score=semantic_score,
        )

    taxonomy_score = calculate_taxonomy_score(
        context=context,
        candidate=candidate,
    )
    difficulty_score = calculate_difficulty_score(
        context=context,
        candidate=candidate,
    )
    skill_score = calculate_skill_score(
        context=context,
        candidate=candidate,
    )

    final_score = (
        0.50 * semantic_score
        + 0.20 * taxonomy_score
        + 0.15 * formula_score
        + 0.10 * difficulty_score
        + 0.05 * skill_score
    )

    return HybridScoreBreakdown(
        semantic_score=semantic_score,
        taxonomy_score=taxonomy_score,
        formula_score=formula_score,
        difficulty_score=difficulty_score,
        skill_score=skill_score,
        final_score=clamp_score(final_score),
    )