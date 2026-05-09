import asyncio

from infra.db.repositories.documents import DocumentRepository
from infra.db.session import AsyncSessionLocal


async def main() -> None:
    async with AsyncSessionLocal() as session:
        repo = DocumentRepository(session)

        document = await repo.create_document(
            filename="sample.md",
            content_type="text/markdown",
            size_bytes=128,
            source_type="markdown",
        )

        print("Created document:", document.id, document.status)

        found = await repo.get_document(document.id)
        print("Found document:", found.id, found.filename, found.status)

        await repo.save_markdown(
            found,
            "# Sample\n\nThis is a test markdown document.\n",
        )

        updated = await repo.get_document(document.id)
        print("Updated document:", updated.status)
        print("Checksum:", updated.markdown_checksum)


if __name__ == "__main__":
    asyncio.run(main())
