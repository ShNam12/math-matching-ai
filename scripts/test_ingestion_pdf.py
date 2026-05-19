import asyncio
from pathlib import Path

from infra.db.repositories.documents import DocumentRepository
from infra.db.session import AsyncSessionLocal
from infra.storage.r2_client import R2StorageClient
from modules.ingestion.service import IngestionService


async def main() -> None:
    pdf_path = Path("data/samples/sample.pdf")

    if not pdf_path.exists():
        raise FileNotFoundError(f"Missing sample PDF: {pdf_path}")

    file_bytes = pdf_path.read_bytes()

    async with AsyncSessionLocal() as session:
        repo = DocumentRepository(session)

        document = await repo.create_document(
            filename=pdf_path.name,
            content_type="application/pdf",
            size_bytes=len(file_bytes),
            source_type="pdf",
        )

        ingestion = IngestionService(
            document_repository=repo,
            storage_client=R2StorageClient(),
        )

        await ingestion.ingest_document(
            document_id=document.id,
            filename=document.filename,
            content_type=document.content_type,
            file_bytes=file_bytes,
        )

        updated = await repo.get_document(document.id)

        print("ID:", updated.id)
        print("Status:", updated.status)
        print("R2 key:", updated.r2_original_key)
        print("Checksum:", updated.markdown_checksum)
        print("Markdown length:", len(updated.markdown_content or ""))
        print("Markdown preview:")
        print((updated.markdown_content or "")[:2000])


if __name__ == "__main__":
    asyncio.run(main())