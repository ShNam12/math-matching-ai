from types import SimpleNamespace

from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.v1.endpoints import documents as documents_endpoint


class FakeDocumentRepository:
    def __init__(self, document=None) -> None:
        self.document = document

    async def get_document(self, document_id: str):
        if self.document is None:
            return None

        if self.document.id != document_id:
            return None

        return self.document


class FakeQuestionRepository:
    def __init__(self, questions=None) -> None:
        self.questions = questions or []
        self.pending_document_id = None
        self.updated = []
        self.failed = []

    async def list_by_document(self, document_id: str):
        return [
            question
            for question in self.questions
            if question.document_id == document_id
        ]

    async def mark_classification_pending_for_document(
        self,
        document_id: str,
    ) -> None:
        self.pending_document_id = document_id

    async def update_classification(
        self,
        question,
        *,
        result,
        classification_model: str,
    ) -> None:
        self.updated.append(
            {
                "question_id": question.id,
                "result": result,
                "classification_model": classification_model,
            }
        )
        question.classification_status = "completed"
        question.embedding_status = "completed"

        return question

    async def mark_classification_failed(
        self,
        question,
        *,
        error_message: str,
        classification_model: str,
    ) -> None:
        self.failed.append(
            {
                "question_id": question.id,
                "error_message": error_message,
                "classification_model": classification_model,
            }
        )


class FakeClassificationService:
    def __init__(self, *, failed_question_ids=None) -> None:
        self.failed_question_ids = set(failed_question_ids or [])
        self.question_ids = []

    def classify_question(self, question):
        self.question_ids.append(question.id)

        if question.id in self.failed_question_ids:
            raise RuntimeError(f"classification failed: {question.id}")

        return SimpleNamespace(label="fake-result")


def test_classify_document_endpoint_returns_success_and_failed_counts(
    monkeypatch,
) -> None:

    synced_question_ids = []

    async def fake_sync_question_payload(question):
        synced_question_ids.append(question.id)    

    fake_document_repository = FakeDocumentRepository(
        SimpleNamespace(id="document-id")
    )
    fake_question_repository = FakeQuestionRepository(
        [
            SimpleNamespace(id="q1", document_id="document-id"),
            SimpleNamespace(id="q2", document_id="document-id"),
        ]
    )
    fake_classification_service = FakeClassificationService(
        failed_question_ids={"q2"}
    )

    monkeypatch.setattr(
        documents_endpoint,
        "DocumentRepository",
        lambda session: fake_document_repository,
    )
    monkeypatch.setattr(
        documents_endpoint,
        "QuestionRepository",
        lambda session: fake_question_repository,
    )
    monkeypatch.setattr(
        documents_endpoint,
        "GeminiQuestionClassifier",
        lambda: object(),
    )
    monkeypatch.setattr(
        documents_endpoint,
        "QuestionClassificationService",
        lambda *, classifier: fake_classification_service,
    )

    monkeypatch.setattr(
        documents_endpoint,
        "try_sync_question_classification_payload",
        fake_sync_question_payload,
    )

    client = TestClient(app)
    response = client.post("/documents/document-id/classify")

    assert response.status_code == 200

    payload = response.json()
    assert payload == {
        "document_id": "document-id",
        "question_count": 2,
        "success_count": 1,
        "failed_count": 1,
    }

    assert fake_question_repository.pending_document_id == "document-id"
    assert fake_classification_service.question_ids == ["q1", "q2"]
    assert [
        item["question_id"]
        for item in fake_question_repository.updated
    ] == ["q1"]
    assert [
        item["question_id"]
        for item in fake_question_repository.failed
    ] == ["q2"]
    assert "classification failed: q2" in (
        fake_question_repository.failed[0]["error_message"]
    )

    assert synced_question_ids == ["q1"]

def test_classify_document_endpoint_returns_404_for_missing_document(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        documents_endpoint,
        "DocumentRepository",
        lambda session: FakeDocumentRepository(None),
    )

    client = TestClient(app)
    response = client.post("/documents/missing/classify")

    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_classify_document_endpoint_rejects_document_without_questions(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        documents_endpoint,
        "DocumentRepository",
        lambda session: FakeDocumentRepository(
            SimpleNamespace(id="empty-document")
        ),
    )
    monkeypatch.setattr(
        documents_endpoint,
        "QuestionRepository",
        lambda session: FakeQuestionRepository([]),
    )

    client = TestClient(app)
    response = client.post("/documents/empty-document/classify")

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "No segmented questions were found: empty-document"
    )
