from datetime import UTC, datetime

from apps.api.v1.endpoints.questions import to_question_response
from infra.db.models import Question


def test_to_question_response_maps_classification_metadata() -> None:
    now = datetime.now(UTC)

    question = Question(
        id="question-1",
        document_id="document-1",
        sequence_number=1,
        marker="Bài",
        marker_number="1",
        statement="Tính tích phân bằng phương pháp từng phần.",
        solution=None,
        answer=None,
        formulas=[
            {
                "latex": r"\int x e^x dx",
                "normalized_latex": r"\int x e^x dx",
                "source": "statement",
            }
        ],
        subject="Giải tích 1",
        subject_code="CALCULUS_1",
        chapter="Chương 2: Phép tính tích phân hàm một biến số",
        chapter_code="GT1_C2_Integral_Calculus_One_Variable",
        chapter_name="Chương 2: Phép tính tích phân hàm một biến số",
        topic_code="GT1_C2_01_Indefinite_Integrals",
        topic_name="Tích phân bất định",
        problem_type_code=(
            "GT1_C2_01_T03_Integration_By_Parts"
        ),
        problem_type_name="Tích phân từng phần",
        difficulty="medium",
        skills=[
            "integration_by_parts",
            "indefinite_integral",
        ],
        taxonomy_id="calculus_1_hust_mi1111",
        taxonomy_version="1.0.0",
        taxonomy_confidence=0.95,
        taxonomy_reason=(
            "Đề bài sử dụng phương pháp tích phân từng phần."
        ),
        review_status="auto_accept",
        classification_status="completed",
        classification_model="fake-model",
        classification_error=None,
        classified_at=now,
        embedding_status="completed",
        embedding_model="fake-embedding-model",
        embedding_dimension=768,
        embedding_error=None,
        embedded_at=now,
        created_at=now,
        updated_at=now,
    )

    response = to_question_response(question)

    assert response.id == question.id
    assert response.document_id == question.document_id

    assert response.subject_code == question.subject_code

    assert response.chapter_code == question.chapter_code
    assert response.chapter_name == question.chapter_name
    assert response.topic_code == question.topic_code
    assert response.topic_name == question.topic_name
    assert (
        response.problem_type_code
        == question.problem_type_code
    )
    assert (
        response.problem_type_name
        == question.problem_type_name
    )

    assert response.difficulty == question.difficulty
    assert response.skills == question.skills

    assert response.taxonomy_id == question.taxonomy_id
    assert response.taxonomy_version == question.taxonomy_version
    assert (
        response.taxonomy_confidence
        == question.taxonomy_confidence
    )
    assert response.taxonomy_reason == question.taxonomy_reason
    assert response.review_status == question.review_status

    assert response.classification_status == "completed"
    assert (
        response.classification_model
        == question.classification_model
    )
    assert response.classification_error is None
    assert response.classified_at == question.classified_at

    assert len(response.formulas) == 1
    assert response.formulas[0].latex == r"\int x e^x dx"