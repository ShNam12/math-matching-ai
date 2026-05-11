from infra.db.repositories.documents import DocumentRepository
from infra.storage.r2_client import R2StorageClient
from modules.ingestion.markdown_processing.normalizer import normalize_markdown
from modules.ingestion.pdf_processing.gemini_pdf_converter import convert_pdf_to_markdown


class IngestionService:
    def __init__(
        self,
        *,
        document_repository: DocumentRepository,
        storage_client: R2StorageClient,
    ) -> None:
        self.document_repository = document_repository
        self.storage_client = storage_client

    async def ingest_document(
        self,
        *,
        document_id: str,
        filename: str,
        content_type: str | None,
        file_bytes: bytes,
    ) -> None:
        document = await self.document_repository.get_document(document_id)

        if document is None:
            raise ValueError(f"Document not found: {document_id}")

        try:
            await self.document_repository.update_status(document, "processing")

            original_key = f"documents/{document_id}/original/{filename}"
            original_url = self.storage_client.upload_bytes(
                key=original_key,
                content=file_bytes,
                content_type=content_type,
            )

            await self.document_repository.save_r2_original(
                document,
                r2_original_key=original_key,
                r2_original_url=original_url,
            )

            if document.source_type == "markdown":
                raw_markdown = file_bytes.decode("utf-8")
            elif document.source_type == "pdf":
                raw_markdown = await convert_pdf_to_markdown(
                    filename=filename,
                    content=file_bytes,
                )
            else:
                raise ValueError(f"Unsupported source type: {document.source_type}")

            markdown = normalize_markdown(raw_markdown)

            await self.document_repository.save_markdown(
                document,
                markdown,
            )

        except Exception as exc:
            await self.document_repository.mark_failed(
                document,
                str(exc),
            )
            raise
