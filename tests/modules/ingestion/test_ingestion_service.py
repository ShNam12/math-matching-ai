import asyncio
from types import SimpleNamespace

import pytest

import modules.ingestion.service as ingestion_module
from modules.ingestion.service import IngestionService


class FakeDocumentRepository:
    def __init__(self) -> None:
        self.document = SimpleNamespace(
            id="document-id",
            source_type="pdf",
            status="uploaded",
            error_message=None,
        )

    async def get_document(self, document_id: str):
        return self.document

    async def update_status(self, document, status: str):
        document.status = status
        return document

    async def save_r2_original(self, document, **kwargs):
        return document

    async def save_markdown(self, document, markdown: str):
        document.status = "completed"
        return document

    async def mark_failed(self, document, error_message: str):
        document.status = "failed"
        document.error_message = error_message
        return document


class FakeStorageClient:
    def upload_bytes(self, **kwargs):
        return None


def test_converter_error_marks_document_failed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_converter(**kwargs):
        raise RuntimeError("Gemini conversion failed")

    monkeypatch.setattr(
        ingestion_module,
        "convert_pdf_to_markdown",
        fake_converter,
    )

    repository = FakeDocumentRepository()
    ingestion = IngestionService(
        document_repository=repository,
        storage_client=FakeStorageClient(),
    )

    with pytest.raises(RuntimeError, match="Gemini conversion failed"):
        asyncio.run(
            ingestion.ingest_document(
                document_id="document-id",
                filename="sample.pdf",
                content_type="application/pdf",
                file_bytes=b"%PDF sample",
            )
        )

    assert repository.document.status == "failed"
    assert repository.document.error_message == "Gemini conversion failed"