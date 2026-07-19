from modules.semantic_search import (
    HybridMatchingCandidate,
    HybridMatchingContext,
    calculate_choice_structure_score,
    calculate_hybrid_score,
    calculate_taxonomy_score,
)


def test_same_problem_type_has_highest_taxonomy_score() -> None:
    context = HybridMatchingContext(
        chapter_code="chapter",
        topic_code="topic",
        problem_type_code="problem_type",
    )
    candidate = HybridMatchingCandidate(
        semantic_score=0.5,
        chapter_code="chapter",
        topic_code="topic",
        problem_type_code="problem_type",
    )

    assert calculate_taxonomy_score(
        context=context,
        candidate=candidate,
    ) == 1.0


def test_same_topic_has_medium_taxonomy_score() -> None:
    context = HybridMatchingContext(
        chapter_code="chapter",
        topic_code="topic",
        problem_type_code="target_problem_type",
    )
    candidate = HybridMatchingCandidate(
        semantic_score=0.5,
        chapter_code="chapter",
        topic_code="topic",
        problem_type_code="other_problem_type",
    )

    assert calculate_taxonomy_score(
        context=context,
        candidate=candidate,
    ) == 0.7


def test_same_chapter_has_low_taxonomy_score() -> None:
    context = HybridMatchingContext(
        chapter_code="chapter",
        topic_code="topic_a",
    )
    candidate = HybridMatchingCandidate(
        semantic_score=0.5,
        chapter_code="chapter",
        topic_code="topic_b",
    )

    assert calculate_taxonomy_score(
        context=context,
        candidate=candidate,
    ) == 0.4


def test_different_chapter_has_zero_taxonomy_score() -> None:
    context = HybridMatchingContext(
        chapter_code="chapter_a",
    )
    candidate = HybridMatchingCandidate(
        semantic_score=0.5,
        chapter_code="chapter_b",
    )

    assert calculate_taxonomy_score(
        context=context,
        candidate=candidate,
    ) == 0.0


def test_difficulty_match_increases_final_score() -> None:
    context = HybridMatchingContext(difficulty="medium")
    matching_candidate = HybridMatchingCandidate(
        semantic_score=0.5,
        difficulty="medium",
    )
    non_matching_candidate = HybridMatchingCandidate(
        semantic_score=0.5,
        difficulty="hard",
    )

    matching_score = calculate_hybrid_score(
        context=context,
        candidate=matching_candidate,
    )
    non_matching_score = calculate_hybrid_score(
        context=context,
        candidate=non_matching_candidate,
    )

    assert matching_score.difficulty_score == 1.0
    assert matching_score.final_score > non_matching_score.final_score


def test_skill_overlap_increases_final_score() -> None:
    context = HybridMatchingContext(
        skills=["derivative", "chain_rule"],
    )
    matching_candidate = HybridMatchingCandidate(
        semantic_score=0.5,
        skills=["derivative", "chain_rule"],
    )
    non_matching_candidate = HybridMatchingCandidate(
        semantic_score=0.5,
        skills=["integral"],
    )

    matching_score = calculate_hybrid_score(
        context=context,
        candidate=matching_candidate,
    )
    non_matching_score = calculate_hybrid_score(
        context=context,
        candidate=non_matching_candidate,
    )

    assert matching_score.skill_score == 1.0
    assert matching_score.final_score > non_matching_score.final_score


def test_final_score_is_clamped_to_valid_range() -> None:
    context = HybridMatchingContext(
        chapter_code="chapter",
        topic_code="topic",
        problem_type_code="problem_type",
        difficulty="easy",
        skills=["skill"],
    )
    candidate = HybridMatchingCandidate(
        semantic_score=2.0,
        chapter_code="chapter",
        topic_code="topic",
        problem_type_code="problem_type",
        difficulty="easy",
        skills=["skill"],
        formula_score=2.0,
        question_type="multiple_choice",
        choice_count=4,
        answer_type="number",
    )

    score = calculate_hybrid_score(
        context=context,
        candidate=candidate,
    )

    assert 0.0 <= score.final_score <= 1.0
    assert score.semantic_score == 1.0
    assert score.formula_score == 1.0


def test_missing_taxonomy_metadata_does_not_crash() -> None:
    context = HybridMatchingContext(
        chapter_code="chapter",
        topic_code="topic",
        problem_type_code="problem_type",
    )
    candidate = HybridMatchingCandidate(
        semantic_score=0.8,
    )

    score = calculate_hybrid_score(
        context=context,
        candidate=candidate,
    )

    assert score.taxonomy_score == 0.0
    assert score.final_score == 0.8

def test_no_hybrid_context_keeps_semantic_score_as_final_score() -> None:
    context = HybridMatchingContext()
    candidate = HybridMatchingCandidate(
        semantic_score=0.92,
        chapter_code="chapter",
        topic_code="topic",
        problem_type_code="problem_type",
        difficulty="easy",
        skills=["skill"],
    )

    score = calculate_hybrid_score(
        context=context,
        candidate=candidate,
    )

    assert score.semantic_score == 0.92
    assert score.taxonomy_score == 0.0
    assert score.difficulty_score == 0.0
    assert score.skill_score == 0.0
    assert score.final_score == 0.92


def test_same_question_type_increases_choice_structure_score() -> None:
    context = HybridMatchingContext(question_type="multiple_choice")
    matching_candidate = HybridMatchingCandidate(
        semantic_score=0.8,
        question_type="multiple_choice",
    )
    non_matching_candidate = HybridMatchingCandidate(
        semantic_score=0.8,
        question_type="free_response",
    )

    assert calculate_choice_structure_score(
        context=context,
        candidate=matching_candidate,
    ) == 1.0
    assert calculate_choice_structure_score(
        context=context,
        candidate=non_matching_candidate,
    ) == 0.0


def test_mcq_candidate_scores_higher_than_free_response_for_mcq_context() -> None:
    context = HybridMatchingContext(
        question_type="multiple_choice",
        choice_count=4,
        answer_type="number",
    )
    mcq_candidate = HybridMatchingCandidate(
        semantic_score=0.8,
        question_type="multiple_choice",
        choice_count=4,
        answer_type="number",
    )
    free_response_candidate = HybridMatchingCandidate(
        semantic_score=0.8,
        question_type="free_response",
        choice_count=0,
        answer_type="number",
    )

    mcq_score = calculate_hybrid_score(
        context=context,
        candidate=mcq_candidate,
    )
    free_response_score = calculate_hybrid_score(
        context=context,
        candidate=free_response_candidate,
    )

    assert mcq_score.choice_structure_score == 1.0
    assert free_response_score.choice_structure_score < 1.0
    assert mcq_score.final_score > free_response_score.final_score


def test_missing_choices_do_not_crash_choice_structure_score() -> None:
    context = HybridMatchingContext(
        question_type="multiple_choice",
        choice_count=4,
        answer_type="expression",
    )
    candidate = HybridMatchingCandidate(
        semantic_score=0.8,
        question_type="multiple_choice",
        choice_count=None,
        answer_type=None,
    )

    score = calculate_hybrid_score(
        context=context,
        candidate=candidate,
    )

    assert score.choice_structure_score > 0.0
    assert 0.0 <= score.final_score <= 1.0
