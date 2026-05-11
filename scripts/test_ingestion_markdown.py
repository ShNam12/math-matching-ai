import asyncio

from infra.db.repositories.documents import DocumentRepository
from infra.db.session import AsyncSessionLocal
from infra.storage.r2_client import R2StorageClient
from modules.ingestion.service import IngestionService


async def main() -> None:
    file_bytes = b"# Demo\r\n\r\nMath: \\(x^2\\)\r\n"

    async with AsyncSessionLocal() as session:
        repo = DocumentRepository(session)

        document = await repo.create_document(
            filename="demo.md",
            content_type="text/markdown",
            size_bytes=len(file_bytes),
            source_type="markdown",
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
        print("Status:", updated.status)
        print("R2 key:", updated.r2_original_key)
        print("Markdown:")
        print(updated.markdown_content)


if __name__ == "__main__":
    asyncio.run(main())
